import unittest
import os
import numpy as np

import geosoft
import geosoft.gxapi as gxapi
import geosoft.gxpy.gx as gx
import geosoft.gxpy.system as gsys
import geosoft.gxpy.map as gxmap
import geosoft.gxpy.view as gxv
import geosoft.gxpy.geometry as gxgm
import geosoft.gxpy.coordinate_system as gxcs
import geosoft.gxpy.system as gxsys
import geosoft.gxpy.grd as gxgrd
import geosoft.gxpy.agg as gxagg

from geosoft.gxpy.tests import GXPYTest

def new_test_data_map(mapname=None, rescale=1.0):

    if mapname is None:
        mapname = os.path.join(gx.GXpy().temp_folder(), 'test')

    with gxmap.GXmap.new(mapname, overwrite=True) as gmap:
        with gxv.GXview(gmap, "rectangle_test") as view:
            view.start_group('rectangle')
            view.xy_rectangle((gxgm.Point((0, 0)), gxgm.Point((250, 110))), pen=gxv.Pen(line_thick=1))

            p1 = gxgm.Point((5, 5)) * rescale
            p2 = gxgm.Point((100, 100)) * rescale
            poff = gxgm.Point((10, 5)) * rescale
            view.pen = gxv.Pen(fill_color=gxv.C_LT_GREEN)
            view.xy_rectangle((p1, p2))

            view.pen = gxv.Pen(line_style=2, line_pitch=2.0)
            view.xy_line((p1 + poff, p2 - poff))

        with gxv.GXview(gmap, "poly") as view:
            view.start_group('poly')
            plinelist = [[110, 5],
                         [120, 20],
                         [130, 15],
                         [150, 50],
                         [160, 70],
                         [175, 35],
                         [190, 65],
                         [220, 50],
                         [235, 18.5]]
            pp = gxgm.PPoint.from_list(plinelist) * rescale
            view.pen = gxv.Pen(line_style=2, line_pitch=2.0)
            view.xy_poly_line(pp)
            view.pen = gxv.Pen(line_style=4, line_pitch=2.0, line_smooth=gxv.SMOOTH_AKIMA)
            view.xy_poly_line(pp)

            ppp = np.array(plinelist)
            pp = gxgm.PPoint(ppp[3:, :]) * rescale
            view.pen = gxv.Pen(line_style=5, line_pitch=5.0,
                          line_smooth=gxv.SMOOTH_CUBIC,
                          line_color=gxapi.C_RED,
                          line_thick=0.25,
                          fill_color=gxapi.C_LT_BLUE)
            view.xy_poly_line(pp, close=True)

            view.pen = gxv.Pen(fill_color=gxapi.C_LT_GREEN)
            pp = (pp - (100, 0, 0)) / 2 + (100, 0, 0)
            view.xy_poly_line(pp, close=True)
            pp += (0, 25, 0)
            view.pen = gxv.Pen(fill_color=gxapi.C_LT_RED)
            view.xy_poly_line(pp, close=True)

        return gmap.filename

def test_data_map(name=None, data_area=(1000,0,11000,5000)):

    if name is None:
        name = os.path.join(gx.GXpy().temp_folder(), "test")
    gxmap.delete_files(name)
    cs = gxcs.GXcs("WGS 84 / UTM zone 15N")
    return gxmap.GXmap.new(filename=name,
                           data_area=data_area,
                           cs=cs,
                           media="A4",
                           margins=(1.5, 3, 1.5, 1),
                           inside_margin=0.5)

class Test(unittest.TestCase, GXPYTest):

    @classmethod
    def setUpClass(cls):
        GXPYTest.setUpClass(cls, __file__)

    @classmethod
    def tearDownClass(cls):
        GXPYTest.tearDownClass(cls)

    
    @classmethod
    def start(cls, test, test_name):
        parts = os.path.split(__file__)
        test.result_dir = os.path.join(parts[0], 'results', parts[1], test_name)
        cls.gx.log("*** {} > {}".format(parts[1], test_name))

    def test_version(self):
        Test.start(self, gsys.func_name())
        self.assertEqual(gxmap.__version__, geosoft.__version__)

    def test_newmap(self):
        Test.start(self, gsys.func_name())

        # test map
        map_name = 'test_newmap'
        gxmap.delete_files(map_name)
        with gxmap.GXmap.new(map_name) as gmap:
            mapfile = gmap.filename
            self.assertEqual(mapfile, os.path.abspath((map_name + '.map')))
        self.assertTrue(os.path.isfile(mapfile))

        # verify can't write on a new map
        self.assertRaises(gxmap.MapException, gxmap.GXmap.new, map_name)
        self.assertRaises(gxmap.MapException, gxmap.GXmap.new, mapfile)
        with gxmap.GXmap.new(map_name, overwrite=True):
            pass

        # but I can open it
        with gxmap.GXmap.open(map_name):
            pass
        with gxmap.GXmap.open(mapfile):
            pass

        gxmap.delete_files(mapfile)
        self.assertFalse(os.path.isfile(mapfile))

        self.assertRaises(gxmap.MapException, gxmap.GXmap, 'bogus')

    def test_new_geosoft_map(self):
        Test.start(self, gsys.func_name())

        # temp map
        with gxmap.GXmap.new(data_area=(0, 0, 100, 80)) as gmap:
            views = gmap.view_list
            self.assertTrue('base' in views)
            self.assertTrue('data' in views)

        with gxmap.GXmap.new(data_area=(0, 0, 100, 80),
                             cs=gxcs.GXcs("DHDN / Okarito 2000 [geodetic]")) as gmap:
            with gxv.GXview(gmap, 'data', mode=gxv.WRITE_OLD) as v:
                self.assertEqual("DHDN / Okarito 2000 [geodetic]", str(v.cs))

    def test_lists(self):
        Test.start(self, gsys.func_name())

        mapname = new_test_data_map()
        with gxmap.GXmap.open(mapname) as gmap:
            views = gmap.view_list
            self.assertTrue('rectangle_test' in views)
            self.assertTrue('poly' in views)

            views = gmap.view_list_2D
            self.assertTrue('rectangle_test' in views)
            self.assertTrue('poly' in views)

            views = gmap.view_list_3D
            self.assertEqual(len(views), 0)

    def test_map_delete(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new(filename='test_geosoft', overwrite=True) as gmap:
            filename = gmap.filename
            self.assertEqual(len(gmap.view_list), 2)
            self.assertTrue(gmap.has_view('data'))
            self.assertTrue(gmap.has_view('base'))
        self.assertTrue(os.path.isfile(filename))
        with open(filename, 'rb') as f:
            pass

        with gxmap.GXmap.new(filename='test_geosoft',
                             overwrite=True,
                             data_area=(1000, 200, 11000, 5000)) as gmap:
            filename = gmap.filename
            self.assertEqual(len(gmap.view_list), 2)
            self.assertTrue(gmap.has_view('data'))
            self.assertTrue(gmap.has_view('base'))
        self.assertTrue(os.path.isfile(filename))
        with open(filename, 'rb') as f:
            pass

        with gxmap.GXmap.new(filename='test_geosoft', overwrite=True) as gmap:
            filename = gmap.filename
            gmap.remove_on_close(True)
        self.assertFalse(os.path.isfile(filename))

        for i in range(3):
            gmap = gxmap.GXmap.new(filename='t{}'.format(i), overwrite=True)
            gmap.remove_on_close(True)
            gmap.close()

    def test_map_classes(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new(filename='test_geosoft', overwrite=True) as gmap:
            self.assertEqual(gmap.get_class_view_name('data'), 'data')
            self.assertEqual(gmap.get_class_view_name('base'), 'base')
            self.assertEqual(gmap.get_class_view_name('section'), 'section')
            self.assertEqual(gmap.get_class_view_name('some_class_name'), 'some_class_name')

            gmap.set_class_view_name('base', 'bogus')
            self.assertEqual(gmap.get_class_view_name('base'), 'bogus')
            gmap.set_class_view_name('data', 'bogus_data')
            #self.assertEqual(gmap.get_class_view_name('data'), 'bogus_data')
            gmap.set_class_view_name('Section', 'yeah')
            self.assertEqual(gmap.get_class_view_name('Section'), 'yeah')
            gmap.set_class_view_name('mine', 'boom')
            self.assertEqual(gmap.get_class_view_name('mine'), 'boom')

        with gxmap.GXmap.new(data_area=(0, 0, 100, 80),
                             cs=gxcs.GXcs("DHDN / Okarito 2000 [geodetic]")) as gmap:

            self.assertEqual(gmap.get_class_view_name('base'), 'base')
            self.assertEqual(gmap.get_class_view_name('data'), 'data')

            with gxv.GXview(gmap, "copy_data", mode=gxv.WRITE_NEW, copy="data"): pass
            gmap.set_class_view_name('data', 'copy_data')
            self.assertEqual(gmap.get_class_view_name('data'), 'copy_data')

    def test_current_view(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new() as map:
            self.assertEqual(map.current_data_view, 'data')
            map.current_data_view = 'base'
            self.assertEqual(map.current_data_view, 'base')
            self.assertEqual(map.get_class_view_name('data'), 'base')
            map.current_data_view = 'data'
            self.assertEqual(map.current_data_view, 'data')
            try:
                map.current_data_view = 'Bogus'
                self.assertTrue(False)
            except gxmap.MapException:
                pass

            map.copy_view('data', 'Bogus')
            map.current_data_view = 'Bogus'
            self.assertEqual(map.current_data_view, 'bogus')
            self.assertRaises(gxmap.MapException, map.copy_view, 'Data', 'bogus')
            self.assertRaises(gxmap.MapException, map.copy_view, 'data', 'bogus')
            map.copy_view('data', 'bogus', overwrite=True)
            self.assertEqual(map.current_data_view, 'bogus')

    def test_media(self):
        Test.start(self, gsys.func_name())

        def crc_media(map_file, test_number):
            with gxmap.GXmap.open(map_file) as map:
                with gxv.GXview(map, "base") as view:
                    view.xy_rectangle(view.extent_clip, pen=gxv.Pen(line_thick=0.2, line_color='K'))
                with gxv.GXview(map, "data") as view:
                    view.xy_rectangle(view.extent_clip, pen=gxv.Pen(line_thick=0.2, line_color='R'))
            self.crc_map(map_file,
                         pix_width=256,
                         alt_crc_name='{}_{}'.format(gxsys.func_name(1), test_number))

        test_media_map = os.path.join(gx.GXpy().temp_folder(), 'test_media')

        test_number = 0
        with gxmap.GXmap.new(test_media_map + 'scale_800', overwrite=True, scale=800,
                             data_area=(5, 10, 50, 100)) as map:
            filename = map.filename
        crc_media(filename, test_number)
        test_number += 1

        with gxmap.GXmap.new(test_media_map + 'scale_100', overwrite=True, scale=100,
                             data_area=(5, 10, 50, 100)) as map:
            filename = map.filename
        crc_media(filename, test_number)
        test_number += 1

        with gxmap.GXmap.new(test_media_map + 'a4_portrait', overwrite=True, media='A4', layout=gxmap.MAP_PORTRAIT) as map:
            filename = map.filename
        crc_media(filename, test_number)
        test_number += 1

        with gxmap.GXmap.new(test_media_map + 'portrait_a4', overwrite=True, media='a4', layout=gxmap.MAP_PORTRAIT) as map:
            filename = map.filename
        crc_media(filename, test_number)
        test_number += 1

        with gxmap.GXmap.new(test_media_map + 'a4_landscape', overwrite=True, media='A4', layout=gxmap.MAP_LANDSCAPE) as map:
            filename = map.filename
        crc_media(filename, test_number)
        test_number += 1

        with gxmap.GXmap.new(test_media_map + 'A4_1', overwrite=True, media='A4', data_area=(10, 5, 100, 50)) as map:
            filename = map.filename
        crc_media(filename, test_number)
        test_number += 1

        with gxmap.GXmap.new(test_media_map + 'A4_2', overwrite=True, media='A4',
                             data_area=(5, 10, 50, 100), layout=gxmap.MAP_LANDSCAPE) as map:
            filename = map.filename
        crc_media(filename, test_number)
        test_number += 1

        with gxmap.GXmap.new(test_media_map + 'A4_3', overwrite=True, media='A4',
                             data_area=(5, 10, 50, 100)) as map:
            filename = map.filename
        crc_media(filename, test_number)
        test_number += 1

        for m in (None, (60, 50), 'unlimited', 'bogus', 'A4', 'A3', 'A2', 'A1', 'A0',
                  'A', 'B', 'C', 'D', 'E'):
            with gxmap.GXmap.new(media=m) as map: pass

        self.assertRaises(gxmap.MapException,
                          gxmap.GXmap.new,
                          test_media_map, overwrite=True, media='A4',
                          data_area=(100, 50, 10, 5), layout='landscape')

    def test_multiple_temp_maps(self):
        Test.start(self, gsys.func_name())

        mapfiles = []
        for i in range(3):
            with gxmap.GXmap.new() as map:
                mapfiles.append(map.filename)
                with gxv.GXview(map, 'data') as v:
                    v.xy_rectangle(v.extent_clip)

        for fn in mapfiles:
            self.assertTrue(os.path.isfile(fn))

    def test_north_arrow_0(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new(cs='ft') as map:
            mapfile = map.filename

            with gxv.GXview(map, 'base') as v:
                v.xy_rectangle(v.extent_clip)
            with gxv.GXview(map, 'data') as v:
                v.xy_rectangle(v.extent_clip)

            map.north_arrow()

        self.crc_map(mapfile)

    def test_north_arrow_1(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new(cs='m', data_area=(0,0,20,10), scale=100) as map:
            mapfile = map.filename

            with gxv.GXview(map, 'base') as v:
                v.xy_rectangle(v.extent_clip)
            with gxv.GXview(map, 'data') as v:
                v.xy_rectangle(v.extent_clip)

            map.north_arrow(location=(2, 0, 3), inclination=-12, declination=74.5,
                            text_def=gxv.Text_def(font='Calibri'))

        self.crc_map(mapfile)


    def test_scale_1(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new(data_area=(350000,7000000,400000,7030000), cs='ft') as map:
            mapfile = map.filename
            with gxv.GXview(map, 'base') as v:
                v.xy_rectangle(v.extent_clip)
            with gxv.GXview(map, 'data') as v:
                v.xy_rectangle(v.extent_clip)
            map.scale_bar()
            map.scale_bar(location=(2, 0, 2), length=10, sections=12)
            map.scale_bar(location=(5, 0, 0), length=8, sections=2, post_scale=True)
            map.scale_bar(location=(3, -3, 1.5), length=4,
                          text=gxv.Text_def(height=0.2, italics=True), post_scale=True)

        self.crc_map(mapfile)

    def test_scale_2(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new(data_area=(350000,7000000,400000,7030000), cs='NAD83 / UTM zone 15N') as map:
            mapfile = map.filename
            with gxv.GXview(map, 'base') as v:
                v.xy_rectangle(v.extent_clip)
            with gxv.GXview(map, 'data') as v:
                v.xy_rectangle(v.extent_clip)
            map.scale_bar()
            map.scale_bar(location=(2, 0, 2), length=10, sections=12)

        self.crc_map(mapfile)


    def test_surround_1(self):
        Test.start(self, gsys.func_name())

        cs = gxcs.GXcs('NAD83 / UTM zone 15N')
        with gxmap.GXmap.new(data_area=(350000, 7000000, 400000, 7030000), cs=cs) as map:
            mapfile = map.filename
            with gxv.GXview(map, 'data') as v:
                v.xy_rectangle(v.extent_clip)
            map.surround()
        self.crc_map(mapfile)

    def test_surround_2(self):
        Test.start(self, gsys.func_name())

        cs = gxcs.GXcs('NAD83 / UTM zone 15N')
        with gxmap.GXmap.new(data_area=(350000, 7000000, 400000, 7030000), cs=cs) as map:
            mapfile = map.filename
            with gxv.GXview(map, 'data') as v:
                v.xy_rectangle(v.extent_clip)
            map.surround(gap=0.2)
        self.crc_map(mapfile)

    def test_surround_3(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new(data_area=(350000, 7000000, 400000, 7030000)) as map:
            mapfile = map.filename
            with gxv.GXview(map, 'data') as v:
                v.xy_rectangle(v.extent_clip)
            map.surround(gap=0.2,
                         outer_pen=gxv.Pen.from_mapplot_string('rt500'),
                         inner_pen=gxv.Pen.from_mapplot_string('K16'))
        self.crc_map(mapfile)

    def test_annotate_xy_0(self):
        Test.start(self, gsys.func_name())

        with test_data_map() as map:
            mapfile = map.filename
            map.annotate_data_xy(x_sep=1500)

        self.crc_map(mapfile)

    def test_annotate_xy_1(self):
        Test.start(self, gsys.func_name())

        with test_data_map() as map:
            mapfile = map.filename
            map.annotate_data_xy(x_sep=1500,
                                 grid=gxmap.GRID_DOTTED,
                                 offset=0.5,
                                 text_def=gxv.Text_def(color='R', weight=gxv.FONT_WEIGHT_BOLD))

        self.crc_map(mapfile)

    def test_annotate_xy_2(self):
        Test.start(self, gsys.func_name())

        with test_data_map() as map:
            mapfile = map.filename
            map.annotate_data_xy(x_sep=1500,
                                 tick=0.1,
                                 text_def=gxv.Text_def(color='G', weight=gxv.FONT_WEIGHT_ULTRALIGHT),
                                 grid=gxmap.GRID_CROSSES,
                                 grid_pen=gxv.Pen(line_color='b', line_thick=0.015))

        self.crc_map(mapfile)

    def test_annotate_xy_3(self):
        Test.start(self, gsys.func_name())

        with test_data_map() as map:
            mapfile = map.filename
            map.annotate_data_xy(x_sep=1500,
                                 tick=0.1,
                                 grid=gxmap.GRID_LINES,
                                 offset=0.2,
                                 edge_pen=gxv.Pen(line_color='k64', line_thick=0.3),
                                 grid_pen=gxv.Pen(line_color='b', line_thick=0.015))

        self.crc_map(mapfile)

    def test_annotate_ll_0(self):
        Test.start(self, gsys.func_name())

        with test_data_map(data_area=(350000,7000000,400000,7030000)) as map:
            mapfile = map.filename
            map.annotate_data_ll()
        self.crc_map(mapfile)

    def test_annotate_ll_1(self):
        Test.start(self, gsys.func_name())

        with test_data_map(data_area=(350000,7000000,400000,7030000)) as map:
            mapfile = map.filename
            map.annotate_data_ll(grid=gxmap.GRID_LINES,
                                 grid_pen=gxv.Pen(line_color='b'),
                                 text_def=gxv.Text_def(color='K127',
                                                       font='cr.gfn',
                                                       weight=gxv.FONT_WEIGHT_BOLD,
                                                       italics=True))
        self.crc_map(mapfile)

    def test_annotate_ll_2(self):
        Test.start(self, gsys.func_name())

        with test_data_map(data_area=(350000,7000000,400000,7030000)) as map:
            mapfile = map.filename
            map.annotate_data_xy()
            map.annotate_data_ll(grid=gxmap.GRID_LINES,
                                  grid_pen=gxv.Pen(line_color='b', line_thick=0.015),
                                  text_def=gxv.Text_def(color='r', height=0.2, italics=True),
                                  top=gxmap.TOP_IN)
        self.crc_map(mapfile)

    def test_annotate_ll_3(self):
        Test.start(self, gsys.func_name())

        with test_data_map(data_area=(350000,7000000,400000,7030000)) as map:
            mapfile = map.filename
            map.annotate_data_xy(tick=0.1, grid=gxmap.GRID_LINES,
                                 text_def=gxv.Text_def(weight=gxv.FONT_WEIGHT_ULTRALIGHT),
                                 grid_pen=gxv.Pen(line_thick=0.01))
            map.annotate_data_ll(grid=gxmap.GRID_LINES,
                                 grid_pen=gxv.Pen(line_color='b', line_thick=0.025),
                                 text_def=gxv.Text_def(height=0.18, italics=True, color='g'))
        self.crc_map(mapfile)

    def test_annotate_ll_4(self):
        Test.start(self, gsys.func_name())

        with test_data_map(data_area=(350000,7000000,400000,7030000)) as map:
            mapfile = map.filename
            map.annotate_data_xy(tick=0.1, grid=gxmap.GRID_LINES,
                                 text_def=gxv.Text_def(weight=gxv.FONT_WEIGHT_BOLD),
                                 top=gxmap.TOP_IN)
            map.annotate_data_ll(grid=gxmap.GRID_LINES,
                                 grid_pen=gxv.Pen(line_color='b', line_thick=0.025),
                                 text_def=gxv.Text_def(height=0.18, italics=True),
                                 top=gxmap.TOP_IN)
        self.crc_map(mapfile)

    def test_color_bar(self):
        Test.start(self, gsys.func_name())

        def test_agg_map():

            # test grid file
            folder, files = gsys.unzip(os.path.join(os.path.dirname(__file__), 'testgrids.zip'),
                                       folder=self.gx.temp_folder())
            grid_file = os.path.join(folder, 'test_agg_utm.grd')
            map_file = os.path.join(self.gx.temp_folder(), "test_agg_utm")

            with gxgrd.GXgrd(grid_file) as grd:
                ex = grd.extent_2d()
                cs = grd.cs
            with gxmap.GXmap.new(map_file, overwrite=True, cs=cs,
                                 data_area=ex, margins=(6,6,5,5)) as gmap:
                mapfile = gmap.filename
                with gxv.GXview(gmap, "data") as v:
                    v.xy_rectangle(v.extent_clip, pen=v.new_pen(line_thick = 0.1, line_color = 'R'))

                    with gxagg.GXagg(grid_file, shade=True) as agg:
                        v.aggregate(agg, name='temp_agg')

                with gxv.GXview(gmap, "data") as v:
                    v.xy_rectangle(v.extent_clip, pen=v.new_pen(line_thick=0.1, line_color='R'))

                with gxv.GXview(gmap, "base") as v:
                    v.xy_rectangle(v.extent_clip, pen=v.new_pen(line_thick = 0.1, line_color = 'B'))

                gmap.annotate_data_ll(grid=gxmap.GRID_LINES,
                                      grid_pen=gxv.Pen.from_mapplot_string("bt250"),
                                      text_def=gxv.Text_def(height=0.25, italics=True),
                                      top=gxmap.TOP_IN)
            return mapfile

        mapfile = test_agg_map()
        with gxmap.GXmap.open(mapfile) as map:
            map.agg_legend()
            with gxv.GXview(map, '*data') as v:
                v.delete_group('temp_agg')
        self.crc_map(mapfile, alt_crc_name='color_bar_0')

        mapfile = test_agg_map()
        with gxmap.GXmap.open(mapfile) as map:
            map.agg_legend(bar_location=gxmap.COLOR_BAR_LEFT,
                           annotation_side=gxmap.COLOR_BAR_ANNOTATE_LEFT,
                           title="Left Bar\nsub_title\n(nano-things)")
            with gxv.GXview(map, '*data') as v:
                v.delete_group('temp_agg')
        self.crc_map(mapfile, alt_crc_name='color_bar_1')

        mapfile = test_agg_map()
        with gxmap.GXmap.open(mapfile) as map:
            map.agg_legend(bar_location=gxmap.COLOR_BAR_BOTTOM,
                           annotation_height=0.5,
                           title='Bottom')
            with gxv.GXview(map, '*data') as v:
                v.delete_group('temp_agg')
        self.crc_map(mapfile, alt_crc_name='color_bar_2')

        mapfile = test_agg_map()
        with gxmap.GXmap.open(mapfile) as map:
            map.agg_legend(bar_location=gxmap.COLOR_BAR_TOP,
                           annotation_side=gxmap.COLOR_BAR_ANNOTATE_BOTTOM,
                           title='This is a Top Centred Bar')
            with gxv.GXview(map, '*data') as v:
                v.delete_group('temp_agg')
        self.crc_map(mapfile, alt_crc_name='color_bar_3')



if __name__ == '__main__':
    unittest.main()