import unittest
import random
import geojson

from decimal import Decimal as D

class TestGeoJSON(unittest.TestCase):
    def assertDictEquals(self, dict1, dict2):
        self.assertTrue(dict1.keys() == dict2.keys())
        for k, v in dict1.iteritems():
            if type(v) is dict:
                self.assertDictEquals(v, dict2[k])
            else:
                self.assertEquals(v, dict2[k])

    def test_point(self):
        data = { "type": "Point", "coordinates": [D('100.0'), D('0.0')] }
        point = geojson.Point()
        point.coordinates = [D('100.0'), D('0.0')]
        self.assertTrue(point.is_valid())
        for key, value in data.iteritems():
            self.assertEquals(getattr(point, key), value)
        self.assertEquals(point.x, D('100.0'))
        self.assertEquals(point.y, D('0.0'))
        self.assertEquals(point.z, None)
        point.coordinates = [D('100.0'), D('0.0'), D('5200.0')]
        self.assertTrue(point.is_valid())
        point.coordinates = [0,1,2,3]
        self.assertTrue(point.is_valid())

    def test_invalid_point(self):
        point = geojson.Point()
        point.coordinates = [0]
        self.assertFalse(point.is_valid())
        point.coordinates = ['foo', 'bar']
        self.assertFalse(point.is_valid())

    def test_linestring(self):
        data = {
            "type": "LineString",
            "coordinates": [[D('100.0'), D('0.0')], [D('101.0'), D('1.0')]]
        }
        linestring = geojson.LineString.from_dict(data)
        self.assertTrue(linestring.is_valid())
        self.assertEquals(data, linestring.to_dict())

    def test_invalid_linestring(self):
        linestring = geojson.LineString()
        linestring.coordinates = [D('100.0'), D('0.0')]
        self.assertFalse(linestring.is_valid())
        linestring.coordinates = [[D('100.0'), D('0.0')]]
        self.assertFalse(linestring.is_valid())
        linestring.coordinates = [[D('100.0')]]
        self.assertFalse(linestring.is_valid())

    def test_multilinestring(self):
        data = {
            "type": "MultiLineString",
            "coordinates": [
                [[D('100.0'), D('0.0')], [D('101.0'), D('1.0')]],
                [[D('102.0'), D('2.0')], [D('103.0'), D('3.0')]]
            ]
        }
        multilinestring = geojson.MultiLineString.from_dict(data)
        self.assertTrue(multilinestring.is_valid())
        self.assertDictEquals(data, multilinestring.to_dict())

    def test_invalid_multilinestring(self):
        multilinestring = geojson.MultiLineString()
        multilinestring.coordinates = [[D('100.0'), D('0.0')]]
        self.assertFalse(multilinestring.is_valid())
        multilinestring.coordinates = [[[D('100.0')], [D('101.0'), D('1.0')]], [[D('102.0'), D('2.0')], [D('103.0'), D('3.0')]]]
        self.assertFalse(multilinestring.is_valid())
        multilinestring.coordinates = []
        self.assertFalse(multilinestring.is_valid())
        multilinestring = geojson.MultiLineString()
        self.assertFalse(multilinestring.is_valid())

    def test_polygon(self):
        data = {
            "type": "Polygon",
            "coordinates": [
                [[D('100.0'), D('0.0')], [D('101.0'), D('0.0')], [D('101.0'), D('1.0')], [D('100.0'), D('1.0')], [D('100.0'), D('0.0')]]
            ]
        }
        polygon = geojson.Polygon.from_dict(data)
        self.assertTrue(polygon.is_valid())
        self.assertDictEquals(data, polygon.to_dict())
        polygon.coordinates = [
            [[D('100.0'), D('0.0')], [D('101.0'), D('0.0')], [D('101.0'), D('1.0')], [D('100.0'), D('1.0')], [D('100.0'), D('0.0')]],
            [[D('100.2'), D('0.2')], [D('100.8'), D('0.2')], [D('100.8'), D('0.8')], [D('100.2'), D('0.8')], [D('100.2'), D('0.2')]]
        ]
        self.assertTrue(polygon.is_valid())

    def test_invalid_polygon(self):
        polygon = geojson.Polygon()
        self.assertFalse(polygon.is_valid())
        polygon.coordinates = []
        self.assertFalse(polygon.is_valid())
        polygon.coordinates = [[[D('100.0'), D('0.0')], [D('101.0'), D('0.0')], [D('100.0')], [D('100.0'), D('0.0')]]]
        self.assertFalse(polygon.is_valid())
        polygon.coordinates = '100.0,0.0'
        self.assertFalse(polygon.is_valid())
        # Don't begin and end at same point.
        polygon.coordinates = [[[D('100.0'), D('0.0')], [D('101.0'), D('0.0')], [D('100.0'), D('1.0')], [D('100.0'), D('2.0')]]]
        self.assertFalse(polygon.is_valid())

    def test_multipolygon(self):
        data = {
            "type": "MultiPolygon",
            "coordinates": [
                [[[D('102.0'), D('2.0')], [D('103.0'), D('2.0')], [D('103.0'), D('3.0')], [D('102.0'), D('3.0')], [D('102.0'), D('2.0')]]],
                [[[D('100.0'), D('0.0')], [D('101.0'), D('0.0')], [D('101.0'), D('1.0')], [D('100.0'), D('1.0')], [D('100.0'), D('0.0')]],
                 [[D('100.2'), D('0.2')], [D('100.8'), D('0.2')], [D('100.8'), D('0.8')], [D('100.2'), D('0.8')], [D('100.2'), D('0.2')]]]
            ]
        }
        multipolygon = geojson.MultiPolygon.from_dict(data)
        self.assertTrue(multipolygon.is_valid())
        self.assertDictEquals(data, multipolygon.to_dict())

    def test_invalid_multipolygon(self):
        multipolygon = geojson.MultiPolygon()
        self.assertFalse(multipolygon.is_valid())
        multipolygon.coordinates = []
        self.assertFalse(multipolygon.is_valid())
        multipolygon.coordinates = [[[[D('102.0'), D('2.0')], [D('103.0'), D('2.0')], [D('102.0'), D('3.0')]]]]
        self.assertFalse(multipolygon.is_valid())

    def test_geometry_collection(self):
        geometries = geojson.GeometryCollection()
        geometries.geometries = [geojson.Point(coordinates=[random.randint(-180, 180), random.randint(-90, 90)]) for _ in xrange(10)]
        self.assertTrue(geometries.is_valid())
        multipolygon = geojson.MultiPolygon()
        multipolygon.coordinates = [
            [[[D('102.0'), D('2.0')], [D('103.0'), D('2.0')], [D('103.0'), D('3.0')], [D('102.0'), D('3.0')], [D('102.0'), D('2.0')]]],
            [[[D('100.0'), D('0.0')], [D('101.0'), D('0.0')], [D('101.0'), D('1.0')], [D('100.0'), D('1.0')], [D('100.0'), D('0.0')]],
             [[D('100.2'), D('0.2')], [D('100.8'), D('0.2')], [D('100.8'), D('0.8')], [D('100.2'), D('0.8')], [D('100.2'), D('0.2')]]]
        ]
        geometries.geometries[4] = multipolygon
        multipolygon = geojson.MultiPolygon()
        multipolygon.coordinates = [[[[D('102.0'), D('2.0')], [D('103.0'), D('2.0')], [D('103.0'), D('3.0')], [D('102.0'), D('3.0')], [D('102.0'), D('2.0')]]]]
        geometries.geometries.append(multipolygon)
        self.assertTrue(geometries.is_valid())
        self.assertEquals(len(geometries), 11)
        for idx, geometry in enumerate(geometries):
            self.assertDictEquals(geometry.to_dict(), geometries[idx].to_dict())

    def test_invalid_geometry_collection(self):
        geometries = geojson.GeometryCollection()
        geometries.geometries = [geojson.Point(coordinates=[0]), geojson.Point(coordinates=[D('100.0'),D('0.0')])]
        self.assertFalse(geometries.is_valid())

    def test_feature(self):
        data = { 
            "type": "Feature", 
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [D('-180.0'), D('10.0')], [D('20.0'), D('90.0')], [D('180.0'), D('-5.0')], [D('-30.0'), D('-90.0')], [D('-180.0'), D('10.0')]
                ]]
            },
            "properties": {
                "name": "Beezlebum",
                "occupation": "Lucador",
                "favorite_color": "chartreuse",
            }
        }
        feature = geojson.Feature.from_dict(data)
        self.assertTrue(feature.is_valid())
        self.assertEquals(feature.type, 'Feature')
        self.assertEquals(feature.geometry.type, 'Polygon')
        self.assertEquals(feature.geometry.coordinates, [[[D('-180.0'), D('10.0')], [D('20.0'), D('90.0')], [D('180.0'), D('-5.0')], [D('-30.0'), D('-90.0')], [D('-180.0'), D('10.0')]]])
        self.assertEquals(feature.properties['name'], 'Beezlebum')
        self.assertEquals(feature.properties['occupation'], 'Lucador')
        self.assertEquals(feature.properties['favorite_color'], 'chartreuse')
        self.assertDictEquals(data, feature.to_dict())
        feature.geometry = None
        self.assertTrue(feature.is_valid())
        feature.properties = None
        self.assertTrue(feature.is_valid())
        data['id'] = 1234
        feature = geojson.Feature.from_dict(data)
        self.assertTrue(feature.is_valid())
        self.assertDictEquals(data, feature.to_dict())

    def test_invalid_feature(self):
        data = {
            "type": "Feature",
            "geometry": {
                "type": "Spaghetti",
                "coordinates": [0,0]
            },
            "properties": {
                "name": "Snarf",
            }
        }
        self.assertRaises(ValueError, lambda: geojson.Feature.from_dict(data))
        data['geometry']['type'] = 'Point'
        data['type'] = 'Feetchor'
        self.assertRaises(ValueError, lambda: geojson.Feature.from_dict(data))

    def test_feature_collection(self):
        data = {
            "type": "FeatureCollection",
            "features": [],
        }
        for _ in xrange(10):
            data['features'].append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [random.randint(-180, 180), random.randint(-90, 90)],
                },
                "properties": None
            })
        feature_collection = geojson.FeatureCollection.from_dict(data)
        self.assertTrue(feature_collection.is_valid())
        self.assertDictEquals(data, feature_collection.to_dict())
        self.assertEquals(len(feature_collection), 10)
        self.assertEquals(len(list(feature_collection)), 10)
        for idx, feature in enumerate(feature_collection):
            self.assertDictEquals(data['features'][idx], feature_collection[idx].to_dict())

    def test_json(self):
        s = '{"type": "Point", "coordinates": [0.0, 0.0]}'
        point = geojson.loads(s)
        self.assertTrue(point.is_valid())
        self.assertEquals(point.type, "Point")
        self.assertEquals(point.coordinates, [D('0.0'), D('0.0')])
        self.assertEquals(geojson.dumps(point), s)
        
    def test_null_value(self):
        s = '{"geometry": {"type": "Point", "coordinates": [-121.48699999999999, 38.577300000000001]}, "properties": {"body": "Sacto 9-1-1: Sacramento child killer among inmates up for parole hearings", "layer": "com.simplegeo.global.fwix", "url": "http://fwix.com/sac/share/c8327dcb32/sacto_9-1-1_sacramento_child_killer_among_inmates_up_for_parole_hearings", "expires": 0, "source": "Sacbee Region", "type": "object", "thumbnail": null}, "type": "Feature", "id": "c8327dcb32", "created": 1267745881}'
        feature = geojson.loads(s)
        self.assertTrue(feature.is_valid())
        self.assertEquals(feature.properties['thumbnail'], None)

if __name__ == '__main__':
    unittest.main()
