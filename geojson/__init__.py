"""
A library for consuming and producing GeoJSON using native Python objects.

GeoJSON is a geospatial data interchange format based on JavaScript Object
Notation (JSON).
"""

try:
    from pyutil import jsonutil as json
    json # just to pacify pyflakes: http://divmod.org/trac/ticket/1499
except ImportError:
    import json

# TODO:
#  - Support for bounding boxes
#  - Support for coordinate reference systems
#  - Collect errors for error reporting


__all__ = ['ValidationError', 'GeoJSON', 'Feature', 'FeatureCollection', 'GeometryCollection', 'Point', 'MultiPoint', 'LineString', 'MultiLineString', 'Polygon', 'MultiPolygon', 'loads', 'dumps']


class ValidationError(Exception):
    def __init__(self, message):
        self.message = message


class DecodeError(ValueError):
    def __init__(self, message):
        self.message = message


classes_by_type = {}

def find_by_type(type):
    """
    Finds and returns the GeoJSON subclass that corresponds to the given type.
    """
    return classes_by_type[type]


def object_from_dict(dct):
    """
    Takes a dictionary representation of a GeoJSON object, finds the Python
    object that corresponds to the `type` attribute, and creates an instance of
    that class using the provided dict.
    """
    try:
        klass = find_by_type(dct.get('type'))
    except KeyError:
        raise DecodeError('Missing or invalid GeoJSON object member: `type`.')
    return klass.from_dict(dct)


def loads(*args, **kwargs):
    dct = json.loads(*args, **kwargs)
    return object_from_dict(dct)


def dumps(obj, *args, **kwargs):
    return json.dumps(obj.to_dict(), *args, **kwargs)


class Field(object):
    """
    A member field of a GeoJSON object.

    If no value is provided, the `default` value will be used. If the field is
    not `required`, and the value is None, then it will not be included in a
    dictionary representation of a GeoJSON object. The `null` attribute
    indicates whether the field can have a null (or None) value.
    """

    def __init__(self, default=None, required=True, null=False):
        self.default = default
        self.required = required
        self.null = null

    def __get__(self, obj, cls):
        if obj is None:
            return self
        if self.attrname not in obj.__dict__:
            if callable(self.default):
                obj.__dict__[self.attrname] = self.default()
            else:
                obj.__dict__[self.attrname] = self.default
        return obj.__dict__[self.attrname]

    def __set__(self, obj, value):
        obj.__dict__[self.attrname] = value

    def validate(self, value):
        if value is None and not self.null and self.required:
            raise ValidationError('Missing required field: %s' % self.attrname)

    def decode(self, value):
        return value

    def encode(self, value):
        return value


class ListField(Field):
    def __init__(self, fld, min_length=None, max_length=None, **kwargs):
        super(ListField, self).__init__(**kwargs)
        self.fld = fld
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value):
        super(ListField, self).validate(value)
        if self.min_length is not None and len(value) < self.min_length:
            raise ValidationError("Value %r is less than min_length %r (it's %r)" %
                    (value, self.min_length, len(value)))
        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError("Value %r is more than max_length %r (it's %r)" %
                    (value, self.max_length, len(value)))
        for v in value:
            self.fld.validate(v) 

    def decode(self, value):
        return [self.fld.decode(v) for v in value]

    def encode(self, value):
        return [self.fld.encode(v) for v in value]


class DictField(Field):
    def __init__(self, **kwargs):
        super(DictField, self).__init__(**kwargs)

    def validate(self, value):
        super(DictField, self).validate(value)
        if value is not None:
            if not hasattr(value, '__getitem__'):
                raise ValidationError('Value of %s (%r) is not a dictionary' % (self.attrname, value))


class ObjectField(Field):
    def __init__(self, cls, **kwargs):
        super(ObjectField, self).__init__(**kwargs)
        self.cls = cls

    def get_cls(self):
        cls = self.__dict__['cls']
        if not callable(cls):
            cls = find_by_type(cls)
        return cls

    def set_cls(self, cls):
        self.__dict__['cls'] = cls

    cls = property(get_cls, set_cls)

    def validate(self, value):
        super(ObjectField, self).validate(value)
        if value is not None:
            for attrname, field in value.fields.iteritems():
                field.validate(getattr(value, attrname))

    def decode(self, value):
        if value is None:
            if callable(self.default):
                return self.default()
            return self.default
        return self.cls.from_dict(value)

    def encode(self, value):
        return value.to_dict()


class PositionField(Field):
    """
    A position is a list of coordinates in x, y, z order (easting, northing,
    altitude for a protjected coordinate reference system, or longitude,
    latitude, altitude for a geographic coordinate system). Any number of
    additional elements are allowed, but their interpretation is not
    standardized.
    """
    def validate(self, value):
        super(PositionField, self).validate(value)
        if not hasattr(value, '__len__') or len(value) < 2:
            raise ValidationError('Value %r are not valid coordinates' % value)
        try:
            lonlat = [float(i) for i in value]
            if lonlat[1] < -90 or lonlat[1] > 90:
                raise ValidationError('Latitude must be between -90 and 90.')
            if lonlat[0] < -180 or lonlat[0] > 180:
                raise ValidationError('Longitude must be between -180 and 180.')
        except (TypeError, ValueError):
            raise ValidationError('Value %r are not valid coordinates' % value)


class LinearRingField(ListField):
    """
    A `LinearRingField` is a closed `LineString` with 4 or more positions. The
    first and last positions must be equivalent.
    """
    def __init__(self, **kwargs):
        super(LinearRingField, self).__init__(PositionField(), min_length=4, **kwargs)

    def validate(self, value):
        super(LinearRingField, self).validate(value)
        if value[0] != value[-1]:
            raise ValidationError('LinearRing must start and end at the same point.')


class PolygonField(ListField):
    def __init__(self, **kwargs):
        super(PolygonField, self).__init__(LinearRingField(), min_length=1, **kwargs)

    def validate(self, value):
        # TODO: Make sure first LinearRing contains all of the rest of the LinearRings.
        super(PolygonField, self).validate(value)


class TypeField(Field):
    def __init__(self, type=None, *args, **kwargs):
        super(TypeField, self).__init__(*args, **kwargs)
        self.type = type

    def __get__(self, obj, value):
        if obj is None:
            return self
        if self.type is None:
            return obj.__class__.__name__
        return self.type

    def __set__(self, obj, value):
        if self.type is None:
            expected = obj.__class__.__name__
        else:
            expected = self.type
        if value != expected:
            raise DecodeError('Value %r is not expected value %r' % (value, expected))


class GeoJSONType(type):
    def __new__(cls, name, bases, attrs):
        fields = {}

        for base in bases:
            if isinstance(base, GeoJSONType):
                fields.update(base.fields)

        # Keep track of all the class attributes that are fields.
        for attrname, field in attrs.items():
            if isinstance(field, Field):
                field.attrname = attrname
                fields[attrname] = field
            elif attrname in fields:
                # Remove any parent fields that subclass redefined as
                # something other than a field.
                del fields[attrname]

        attrs['fields'] = fields
        new_cls = super(GeoJSONType, cls).__new__(cls, name, bases, attrs)
        classes_by_type[name] = new_cls
        return new_cls


class GeoJSON(object):
    """
    A `GeoJSON` object may represent a `Geometry`, a `Feature`, or a
    `FeatureCollection`.

    Attributes:
        `type` (required): represents the GeoJSON object type.
        `crs` (optional): the coordinate reference system of the object.
        `bbox` (optional): a bounding box array.
    """

    __metaclass__ = GeoJSONType

    type = TypeField()
    crs = Field(null=True, required=False)
    bbox = Field(null=True, required=False)

    def __init__(self, **kwargs):
        for name, value in kwargs.iteritems():
            setattr(self, name, value)
        self.errors = []

    def is_valid(self):
        self.errors = []
        for attrname, field in self.fields.iteritems():
            try:
                field.validate(getattr(self, attrname))
            except ValidationError, e:
                self.errors.append(e.message)
        return len(self.errors) == 0

    @classmethod
    def from_dict(cls, dct):
        """
        Takes a dictionary representing a GeoJSON object and returns a native
        Python object representation.

        If invalid data is encountered, a DecodeError may be raised. At this
        stage only limited type checking is done, however, and you should call
        the `is_valid()` method to fully validate the object.
        """
        obj = cls()
        for attrname, field in obj.fields.iteritems():
            value = dct.get(attrname)
            if value is not None or field.null:
                setattr(obj, attrname, field.decode(dct.get(attrname)))
        return obj

    def to_dict(self):
        dct = {}
        for attrname, field in self.fields.iteritems():
            value = field.encode(getattr(self, attrname))
            if value is not None or field.required:
                dct[attrname] = value
        return dct


class Geometry(GeoJSON):
    """
    A `Geometry` is an abstract base class for the various geometry types that
    are representable in GeoJSON. A `Geometry` object always has a `coordinates`
    attribute, although the value of the coordinates attribute differs depending
    on the type of geometry.
    """
    coordinates = PositionField()

    @classmethod
    def from_dict(cls, dct):
        type = dct.get('type')
        try:
            klass = find_by_type(type)
        except KeyError:
            raise DecodeError('Missing or invalid GeoJSON object member: `type`.')
        return super(Geometry, klass).from_dict(dct)


class Feature(GeoJSON):
    """
    A GeoJSON Feature object.

    A feature object must have a attribute `geometry`. The value of the geometry
    attribute is a geometry object or None. 
    
    The `properties` attribute is a dictionary (that can contain any arbitrary
    data) or None.

    If a feature has a commonly used identifier, it should be included as the
    features `id` attribute.
    """
    id = Field(null=True, required=False)
    geometry = ObjectField(Geometry, null=True)
    properties = DictField(null=True)


class FeatureCollection(GeoJSON):
    """
    A GeoJSON FeatureCollection object.

    A feature collection has an attribute `features` that contains a list of
    GeoJSON `Feature` objects.
    """
    features = ListField(ObjectField(Feature))

    def __iter__(self):
        for feature in self.features:
            yield feature

    def __len__(self):
        if self.features:
            return len(self.features)
        return 0

    def __getitem__(self, k):
        if not self.features:
            raise IndexError(k)
        return self.features.__getitem__(k)

    def append(self, feature):
        if self.features is None:
            self.features = []
        self.features.append(feature)


class GeometryCollection(GeoJSON):
    """
    A collection of `Geometry` objects.

    Each element in the list of geometries (the `geometries` attribute) must be
    a GeoJSON `Geometry` object.
    """
    geometries = ListField(ObjectField(Geometry))

    def __iter__(self):
        for geometry in self.geometries:
            yield geometry

    def __len__(self):
        if self.geometries:
            return len(self.geometries)
        return 0

    def __getitem__(self, k):
        if not self.geometries:
            raise IndexError(k)
        return self.geometries.__getitem__(k)

    def append(self, geometry):
        if self.geometries is None:
            self.geometries = []
        self.geometries.append(geometry)


class Point(Geometry):
    """
    A `Geometry` whose coordinates represent a single position.
    """

    @property
    def x(self):
        return self.coordinates[0]

    @property
    def y(self):
        return self.coordinates[1]

    @property
    def z(self):
        return self.coordinates[2] if len(self.coordinates) > 2 else None


class MultiPoint(Geometry):
    """
    A `Geometry` whose coordinates represent a series of positions.
    """
    coordinates = ListField(PositionField())


class LineString(Geometry):
    """
    A `Geometry` whose coordinates represent a line. The `coordinates` attribute
    must be an array of two or more positions.
    """
    coordinates = ListField(PositionField(), min_length=2)


class MultiLineString(Geometry):
    """
    A `Geometry` whose coordinates are a list of `LineStrings`.
    """
    coordinates = ListField(ListField(PositionField(), min_length=2), min_length=1)


class Polygon(Geometry):
    """
    A `Geometry` whose coordinates are a list of linear rings. For `Polygons`
    with multiple rings, the first must be the exterior ring and any others must
    be interior rings or holes.
    """
    coordinates = PolygonField()


class MultiPolygon(Geometry):
    """
    A `Geometry` whose coordinates are an array of `Polygons`.
    """
    coordinates = ListField(PolygonField(), min_length=1)

