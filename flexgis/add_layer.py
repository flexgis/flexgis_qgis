import os
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsMapLayerProxyModel, QgsRasterLayer

# upload layer button
def _add_layer(self):
    layer_name = self.dlg_add_layer.text_name.toPlainText()
    if len(layer_name) > 0:
        layer_description = self.dlg_add_layer.text_description.toPlainText()
        layer_tags_plain = self.dlg_add_layer.text_tags.toPlainText()
        layer_tags = layer_tags_plain.split(",")
        layer_tags_string = ""
        for lt in layer_tags:
            if lt != "":
                layer_tags_string += '"' + lt + '"' + ","

        layer_tags_string = layer_tags_string[:0] + "[" + layer_tags_string[0:-1] + "]"

        isSelected = self.dlg_add_layer.checkBox_selected.isChecked()
        isStyled = self.dlg_add_layer.checkBox_style.isChecked()
        layer_to_add = self.dlg_add_layer.map_layers_cb.currentLayer()

        if isinstance(layer_to_add, QgsRasterLayer):
            # upload raster
            self.layerCopyPath_add = layer_to_add.dataProvider().dataSourceUri()
            data_type = "raster"
        else:
            # create geopackage
            self._create_gpkg_from_layer(layer_to_add, isSelected)
            data_type = "gpkg"

        if os.path.isfile(self.layerCopyPath_add):
            import json
            url_add_layer = '/api/load/user_data/'

            styleDict = {"singleSymbol": "CommonSymbol", "categorizedSymbol":"ByAttribute","graduatedSymbol":"ByAttribute", "Circle":"circle", "Square":"square"}
            styleSttings = {}
            if isStyled and data_type != "raster":
                import urllib.parse
                import re
                import uuid
                lyr_type = layer_to_add.geometryType() #0 1 2
                rend = layer_to_add.renderer()
                lyr_style_type = rend.type()
                if lyr_type == 0: #point
                    if lyr_style_type == "singleSymbol":
                        lyr_symbol = rend.symbol().symbolLayers()[0]
                        lyr_symbol_fill = {"color": {"r": lyr_symbol.color().red(),"g": lyr_symbol.color().green(),"b": lyr_symbol.color().blue(),"a": lyr_symbol.color().alpha()/255.0}}
                        lyr_symbol_stroke =  {"width": lyr_symbol.strokeWidth(), "color": { "a": lyr_symbol.strokeColor().alpha()/255.0, "r": lyr_symbol.strokeColor().red(), "g": lyr_symbol.strokeColor().green(), "b": lyr_symbol.strokeColor().blue() }}
                        name = lyr_symbol.properties()["name"]
                        if name[-4:] == ".svg":
                            lyr_symbol_image_type = "circle"
                            string_svg = ""
                            with open(name,"r") as inSVG:
                                for l in inSVG.readlines():
                                    string_svg+=l.replace("\n","").replace('fill="param(fill)"', f'fill="{lyr_symbol.color().name()}"').replace('stroke="param(outline)"', f'stroke="{lyr_symbol.strokeColor().name()}"')
                            string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{lyr_symbol.size()+10}"', string_svg ) 
                            string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{lyr_symbol.size()+10}"', string_svg )
                        elif name == 'square':
                            lyr_symbol_image_type = "square"
                            string_svg = '<svg width="28" height="28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="28" height="28" fill="#8d5a99" stroke="#232323" stroke-width="0" stroke-dasharray=""></rect></svg>'
                            string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{lyr_symbol.size()+10}"', string_svg ) 
                            string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{lyr_symbol.size()+10}"', string_svg )
                            string_svg = re.sub(r'fill=\"#.*?"',f'fill="{lyr_symbol.color().name()}"', string_svg ) 
                            string_svg = re.sub(r'stroke=\"#.*?"',f'stroke="{lyr_symbol.strokeColor().name()}"', string_svg ) 
                        elif name == 'diamond':
                            lyr_symbol_image_type = "Rhomb"
                            string_svg = '<svg height="25" width="25" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M0.707107 12L12 0.707107L23.2929 12L12 23.2929L0.707107 12Z" fill="#869be4" stroke="#000000" stroke-width="1"></path></svg>'
                            string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{lyr_symbol.size()+10}"', string_svg ) 
                            string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{lyr_symbol.size()+10}"', string_svg )
                            string_svg = re.sub(r'fill=\"#.*?"',f'fill="{lyr_symbol.color().name()}"', string_svg ) 
                            string_svg = re.sub(r'stroke=\"#.*?"',f'stroke="{lyr_symbol.strokeColor().name()}"', string_svg ) 
                        elif name == 'triangle':
                            lyr_symbol_image_type = "Triangle"
                            string_svg = '<svg height="28" width="28" viewBox="0 0 24 22" xmlns="http://www.w3.org/2000/svg"><path d="M12 0.649994L0 21.35H24L12 0.649994Z" fill="#869be4" stroke="#000000" stroke-width="1"></path></svg>'
                            string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{lyr_symbol.size()+10}"', string_svg ) 
                            string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{lyr_symbol.size()+10}"', string_svg )
                            string_svg = re.sub(r'fill=\"#.*?"',f'fill="{lyr_symbol.color().name()}"', string_svg ) 
                            string_svg = re.sub(r'stroke=\"#.*?"',f'stroke="{lyr_symbol.strokeColor().name()}"', string_svg ) 
                        else: #circle
                            lyr_symbol_image_type = "circle"
                            string_svg = '<svg height="10" width="10" viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><circle cx="5" cy="5" r="4.5" stroke="#000000" stroke-width="1" stroke-dasharray="" fill="#fff5f0"></circle></svg>'
                            string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{lyr_symbol.size()+10}"', string_svg )
                            string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{lyr_symbol.size()+10}"', string_svg )
                            string_svg = re.sub(r'viewBox=\".*?"',f'viewBox="0 0 {lyr_symbol.size()+10} {lyr_symbol.size()+10}"', string_svg )
                            string_svg = re.sub(r'cx=\"\d*?.\d*"',f'cx="{(lyr_symbol.size()+10)/2.0}"', string_svg )
                            string_svg = re.sub(r'cy=\"\d*?.\d*"',f'cy="{(lyr_symbol.size()+10)/2.0}"', string_svg )
                            string_svg = re.sub(r'r=\"\d*?.\d*"',f'r="{(lyr_symbol.size()+10)/2.0 - 0.5}"', string_svg )
                            string_svg = re.sub(r'fill=\"#.*?"',f'fill="{lyr_symbol.color().name()}"', string_svg )
                            string_svg = re.sub(r'stroke=\"#.*?"',f'stroke="{lyr_symbol.strokeColor().name()}"', string_svg )
                        string_svg = urllib.parse.quote(string_svg)
                        string_svg = "data:image/svg+xml;utf8," + string_svg
                        lyr_symbol_image = {"size": lyr_symbol.size()+10,"type": lyr_symbol_image_type, "imageString": string_svg}
                        styleSttings = {"style": {"type":styleDict[lyr_style_type], "symbol": {"stroke": lyr_symbol_stroke, "fill": lyr_symbol_fill, "image": lyr_symbol_image}}}
                    elif lyr_style_type == "categorizedSymbol":
                        cat_field = rend.classAttribute()
                        cat_values = []
                        for c in rend.categories():
                            cat_value = c.value()
                            if type(cat_value) is float:
                                if int(cat_value) == cat_value:
                                    cat_value = str(int(cat_value))
                            cat_alias = c.label()
                            cat_symbol = c.symbol().symbolLayers()[0]
                            cat_symbol_fill = {"color": {"r": cat_symbol.color().red(),"g": cat_symbol.color().green(),"b": cat_symbol.color().blue(),"a": cat_symbol.color().alpha()/255.0}}
                            cat_symbol_stroke =  {"width": cat_symbol.strokeWidth(), "color": { "a": cat_symbol.strokeColor().alpha()/255.0, "r": cat_symbol.strokeColor().red(), "g": cat_symbol.strokeColor().green(), "b": cat_symbol.strokeColor().blue() }}
                            name = cat_symbol.properties()["name"]
                            if name[-4:] == ".svg":
                                cat_symbol_image_type = "circle"
                                string_svg = ""
                                with open(name,"r") as inSVG:
                                    for l in inSVG.readlines():
                                        string_svg+=l.replace("\n","").replace('fill="param(fill)"', f'fill="{cat_symbol.color().name()}"').replace('stroke="param(outline)"', f'stroke="{cat_symbol.strokeColor().name()}"')
                                string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{cat_symbol.size()+10}"', string_svg ) 
                                string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{cat_symbol.size()+10}"', string_svg )
                            elif name == 'square':
                                cat_symbol_image_type = "square"
                                string_svg = '<svg width="28" height="28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="28" height="28" fill="#8d5a99" stroke="#232323" stroke-width="0" stroke-dasharray=""></rect></svg>'
                                string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{cat_symbol.size()+10}"', string_svg ) 
                                string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{cat_symbol.size()+10}"', string_svg )
                                string_svg = re.sub(r'fill=\"#.*?"',f'fill="{cat_symbol.color().name()}"', string_svg ) 
                                string_svg = re.sub(r'stroke=\"#.*?"',f'stroke="{cat_symbol.strokeColor().name()}"', string_svg ) 
                            elif name == 'diamond':
                                cat_symbol_image_type = "Rhomb"
                                string_svg = '<svg height="25" width="25" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M0.707107 12L12 0.707107L23.2929 12L12 23.2929L0.707107 12Z" fill="#869be4" stroke="#000000" stroke-width="1"></path></svg>'
                                string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{cat_symbol.size()+10}"', string_svg ) 
                                string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{cat_symbol.size()+10}"', string_svg )
                                string_svg = re.sub(r'fill=\"#.*?"',f'fill="{cat_symbol.color().name()}"', string_svg ) 
                                string_svg = re.sub(r'stroke=\"#.*?"',f'stroke="{cat_symbol.strokeColor().name()}"', string_svg ) 
                            elif name == 'triangle':
                                cat_symbol_image_type = "Triangle"
                                string_svg = '<svg height="28" width="28" viewBox="0 0 24 22" xmlns="http://www.w3.org/2000/svg"><path d="M12 0.649994L0 21.35H24L12 0.649994Z" fill="#869be4" stroke="#000000" stroke-width="1"></path></svg>'
                                string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{cat_symbol.size()+10}"', string_svg ) 
                                string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{cat_symbol.size()+10}"', string_svg )
                                string_svg = re.sub(r'fill=\"#.*?"',f'fill="{cat_symbol.color().name()}"', string_svg ) 
                                string_svg = re.sub(r'stroke=\"#.*?"',f'stroke="{cat_symbol.strokeColor().name()}"', string_svg ) 
                            else: #circle
                                cat_symbol_image_type = "circle"
                                string_svg = '<svg height="10" width="10" viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><circle cx="5" cy="5" r="4.5" stroke="#000000" stroke-width="1" stroke-dasharray="" fill="#fff5f0"></circle></svg>'
                                string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{cat_symbol.size()+10}"', string_svg )
                                string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{cat_symbol.size()+10}"', string_svg )
                                string_svg = re.sub(r'viewBox=\".*?"',f'viewBox="0 0 {cat_symbol.size()+10} {cat_symbol.size()+10}"', string_svg )
                                string_svg = re.sub(r'cx=\"\d*?.\d*"',f'cx="{(cat_symbol.size()+10)/2.0}"', string_svg )
                                string_svg = re.sub(r'cy=\"\d*?.\d*"',f'cy="{(cat_symbol.size()+10)/2.0}"', string_svg )
                                string_svg = re.sub(r'r=\"\d*?.\d*"',f'r="{(cat_symbol.size()+10)/2.0 - 0.5}"', string_svg )
                                string_svg = re.sub(r'fill=\"#.*?"',f'fill="{cat_symbol.color().name()}"', string_svg )
                                string_svg = re.sub(r'stroke=\"#.*?"',f'stroke="{cat_symbol.strokeColor().name()}"', string_svg )
                            string_svg = urllib.parse.quote(string_svg)
                            string_svg = "data:image/svg+xml;utf8," + string_svg
                            cat_symbol_image = {"size": cat_symbol.size()+10,"type": cat_symbol_image_type, "imageString": string_svg}
                            cat_values.append({"id":str(uuid.uuid4()),"value": f"{cat_value}", "alias": cat_alias, "symbol": {"stroke": cat_symbol_stroke, "fill": cat_symbol_fill, "image": cat_symbol_image}})
                        def_type = {"stroke": {	"width": 1,	"color": {"a": 1,"r": 0,"g": 0,"b": 0}},"fill": {"color": {"a": 1,"r": 134,"g": 155,"b": 228}},"image": {"size": 15,"type": "circle","imageString": "data:image/svg+xml;utf8,%3Csvg%20height%3D%2215%22%20width%3D%2215%22%20viewBox%3D%220%200%2015%2015%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Ccircle%20cx%3D%227.5%22%20cy%3D%227.5%22%20r%3D%227%22%20stroke%3D%22%23000000%22%20stroke-width%3D%221%22%20stroke-dasharray%3D%22%22%20fill%3D%22%23869be4%22%3E%3C%2Fcircle%3E%3C%2Fsvg%3E"}}
                        styleSttings = {"style": {"type":styleDict[lyr_style_type], "fieldName": cat_field, "symbolValueType": "Value", "values": cat_values, "defaultSymbol": def_type, "removeDefaultFromLegend": True}}
                    elif lyr_style_type ==  "graduatedSymbol":
                        ran_field = rend.classAttribute()
                        ran_values = []
                        for r in rend.ranges():
                            min_value = int(r.lowerValue())
                            max_value = int(r.upperValue())+1
                            ran_alias = r.label()
                            ran_symbol = r.symbol().symbolLayers()[0]
                            ran_symbol_fill = {"color": {"r": ran_symbol.color().red(),"g": ran_symbol.color().green(),"b": ran_symbol.color().blue(),"a": ran_symbol.color().alpha()/255.0}}
                            ran_symbol_stroke =  {"width": ran_symbol.strokeWidth(), "color": { "a": ran_symbol.strokeColor().alpha()/255.0, "r": ran_symbol.strokeColor().red(), "g": ran_symbol.strokeColor().green(), "b": ran_symbol.strokeColor().blue() }}
                            name = ran_symbol.properties()["name"]
                            if name[-4:] == ".svg":
                                ran_symbol_image_type = "circle"
                                string_svg = ""
                                with open(name,"r") as inSVG:
                                    for l in inSVG.readlines():
                                        string_svg+=l.replace("\n","").replace('fill="param(fill)"', f'fill="{ran_symbol.color().name()}"').replace('stroke="param(outline)"', f'stroke="{ran_symbol.strokeColor().name()}"')
                                string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{ran_symbol.size()+10}"', string_svg ) 
                                string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{ran_symbol.size()+10}"', string_svg )
                            elif name == 'square':
                                ran_symbol_image_type = "square"
                                string_svg = '<svg width="28" height="28" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="28" height="28" fill="#8d5a99" stroke="#232323" stroke-width="0" stroke-dasharray=""></rect></svg>'
                                string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{ran_symbol.size()+10}"', string_svg ) 
                                string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{ran_symbol.size()+10}"', string_svg )
                                string_svg = re.sub(r'fill=\"#.*?"',f'fill="{ran_symbol.color().name()}"', string_svg ) 
                                string_svg = re.sub(r'stroke=\"#.*?"',f'stroke="{ran_symbol.strokeColor().name()}"', string_svg ) 
                            elif name == 'diamond':
                                ran_symbol_image_type = "Rhomb"
                                string_svg = '<svg height="25" width="25" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M0.707107 12L12 0.707107L23.2929 12L12 23.2929L0.707107 12Z" fill="#869be4" stroke="#000000" stroke-width="1"></path></svg>'
                                string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{ran_symbol.size()+10}"', string_svg ) 
                                string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{ran_symbol.size()+10}"', string_svg )
                                string_svg = re.sub(r'fill=\"#.*?"',f'fill="{ran_symbol.color().name()}"', string_svg ) 
                                string_svg = re.sub(r'stroke=\"#.*?"',f'stroke="{ran_symbol.strokeColor().name()}"', string_svg ) 
                            elif name == 'triangle':
                                ran_symbol_image_type = "Triangle"
                                string_svg = '<svg height="28" width="28" viewBox="0 0 24 22" xmlns="http://www.w3.org/2000/svg"><path d="M12 0.649994L0 21.35H24L12 0.649994Z" fill="#869be4" stroke="#000000" stroke-width="1"></path></svg>'
                                string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{ran_symbol.size()+10}"', string_svg ) 
                                string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{ran_symbol.size()+10}"', string_svg )
                                string_svg = re.sub(r'fill=\"#.*?"',f'fill="{ran_symbol.color().name()}"', string_svg ) 
                                string_svg = re.sub(r'stroke=\"#.*?"',f'stroke="{ran_symbol.strokeColor().name()}"', string_svg ) 
                            else: #circle
                                ran_symbol_image_type = "circle"
                                string_svg = '<svg height="10" width="10" viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><circle cx="5" cy="5" r="4.5" stroke="#000000" stroke-width="1" stroke-dasharray="" fill="#fff5f0"></circle></svg>'
                                string_svg = re.sub(r' width=\"\d*?.\d*"',f' width="{ran_symbol.size()+10}"', string_svg )
                                string_svg = re.sub(r'height=\"\d*?.\d*"',f'height="{ran_symbol.size()+10}"', string_svg )
                                string_svg = re.sub(r'viewBox=\".*?"',f'viewBox="0 0 {ran_symbol.size()+10} {ran_symbol.size()+10}"', string_svg )
                                string_svg = re.sub(r'cx=\"\d*?.\d*"',f'cx="{(ran_symbol.size()+10)/2.0}"', string_svg )
                                string_svg = re.sub(r'cy=\"\d*?.\d*"',f'cy="{(ran_symbol.size()+10)/2.0}"', string_svg )
                                string_svg = re.sub(r'r=\"\d*?.\d*"',f'r="{(ran_symbol.size()+10)/2.0 - 0.5}"', string_svg )
                                string_svg = re.sub(r'fill=\"#.*?"',f'fill="{ran_symbol.color().name()}"', string_svg )
                                string_svg = re.sub(r'stroke=\"#.*?"',f'stroke="{ran_symbol.strokeColor().name()}"', string_svg )
                            string_svg = urllib.parse.quote(string_svg)
                            string_svg = "data:image/svg+xml;utf8," + string_svg
                            ran_symbol_image = {"size": ran_symbol.size()+10,"type": ran_symbol_image_type, "imageString": string_svg}
                            ran_values.append({"type": "Range","id":str(uuid.uuid4()),"minValue": f"{min_value}","maxValue": f"{max_value}", "alias": ran_alias, "symbol": {"stroke": ran_symbol_stroke, "fill": ran_symbol_fill, "image":ran_symbol_image}})
                        def_type = {"stroke": {	"width": 1,	"color": {"a": 1,"r": 0,"g": 0,"b": 0}},"fill": {"color": {"a": 1,"r": 134,"g": 155,"b": 228}},"image": {"size": 15,"type": "circle","imageString": "data:image/svg+xml;utf8,%3Csvg%20height%3D%2215%22%20width%3D%2215%22%20viewBox%3D%220%200%2015%2015%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Ccircle%20cx%3D%227.5%22%20cy%3D%227.5%22%20r%3D%227%22%20stroke%3D%22%23000000%22%20stroke-width%3D%221%22%20stroke-dasharray%3D%22%22%20fill%3D%22%23869be4%22%3E%3C%2Fcircle%3E%3C%2Fsvg%3E"}}
                        styleSttings = {"style": {"type":styleDict[lyr_style_type], "fieldName": ran_field, "symbolValueType": "Range", "values": ran_values, "defaultSymbol": def_type, "removeDefaultFromLegend": True}}
                elif lyr_type == 1: #line
                    if lyr_style_type == "singleSymbol":
                        lyr_symbol = rend.symbol().symbolLayers()[0]
                        lyr_symbol_fill = {"color": {"r": lyr_symbol.color().red(),"g": lyr_symbol.color().green(),"b": lyr_symbol.color().blue(),"a": lyr_symbol.color().alpha()/255.0}}
                        lyr_symbol_stroke =  {"width": lyr_symbol.width(), "color": { "a": lyr_symbol.color().alpha()/255.0, "r": lyr_symbol.color().red(), "g": lyr_symbol.color().green(), "b": lyr_symbol.color().blue() }}
                        styleSttings = {"style": {"type":styleDict[lyr_style_type], "symbol": {"stroke": lyr_symbol_stroke, "fill": lyr_symbol_fill}}}
                    elif lyr_style_type == "categorizedSymbol":
                        cat_field = rend.classAttribute()
                        cat_values = []
                        for c in rend.categories():
                            cat_value = c.value()
                            if type(cat_value) is float:
                                if int(cat_value) == cat_value:
                                    cat_value = str(int(cat_value))
                            cat_alias = c.label()
                            cat_symbol = c.symbol().symbolLayers()[0]
                            lyr_symbol_fill = {"color": {"r": cat_symbol.color().red(),"g":  cat_symbol.color().green(),"b":  cat_symbol.color().blue(),"a":  cat_symbol.color().alpha()/255.0}}
                            lyr_symbol_stroke =  {"width": cat_symbol.width(), "color": { "a": cat_symbol.color().alpha()/255.0, "r": cat_symbol.color().red(), "g": cat_symbol.color().green(), "b": cat_symbol.color().blue() }}
                            cat_values.append({"type":"Value", "id":str(uuid.uuid4()),"value": f"{cat_value}", "alias": cat_alias, "symbol": {"stroke": lyr_symbol_stroke, "fill": lyr_symbol_fill}})
                        def_type = {"stroke": {"width": 1,"color": {"a": 1,"r": 0,"g": 0,"b": 0}},"fill": {"color": {"a": 1,"r": 134,"g": 155,"b": 228}}}
                        styleSttings = {"style": {"type":styleDict[lyr_style_type], "fieldName": cat_field, "symbolValueType": "Value", "values": cat_values, "defaultSymbol": def_type, "removeDefaultFromLegend": True}}
                    elif lyr_style_type ==  "graduatedSymbol":
                        ran_field = rend.classAttribute()
                        ran_values = []
                        for r in rend.ranges():
                            min_value = int(r.lowerValue())
                            max_value = int(r.upperValue())+1
                            ran_alias = r.label()
                            ran_symbol = r.symbol().symbolLayers()[0]
                            lyr_symbol_fill = {"color": {"r": ran_symbol.color().red(),"g":  ran_symbol.color().green(),"b":  ran_symbol.color().blue(),"a":  ran_symbol.color().alpha()/255.0}}
                            lyr_symbol_stroke =  {"width": ran_symbol.width(), "color": { "a": ran_symbol.color().alpha()/255.0, "r": ran_symbol.color().red(), "g": ran_symbol.color().green(), "b": ran_symbol.color().blue() }}
                            ran_values.append({"type": "Range","id":str(uuid.uuid4()),"minValue": f"{min_value}","maxValue": f"{max_value}", "alias": ran_alias, "symbol": {"stroke": lyr_symbol_stroke, "fill": lyr_symbol_fill}})
                        def_type = {"stroke": {"width": 1,"color": {"a": 1,"r": 0,"g": 0,"b": 0}},"fill": {"color": {"a": 1,"r": 134,"g": 155,"b": 228}}}
                        styleSttings = {"style": {"type":styleDict[lyr_style_type], "fieldName": ran_field, "symbolValueType": "Range", "values": ran_values, "defaultSymbol": def_type, "removeDefaultFromLegend": True}}
                elif lyr_type == 2: #polygon
                    if lyr_style_type == "singleSymbol":
                        lyr_symbol = rend.symbol().symbolLayers()[0]
                        lyr_symbol_fill = {"color": {"r": lyr_symbol.color().red(),"g": lyr_symbol.color().green(),"b": lyr_symbol.color().blue(),"a": lyr_symbol.color().alpha()/255.0},"type": "solid"}
                        lyr_symbol_stroke =  {"width": lyr_symbol.strokeWidth(), "color": { "a": lyr_symbol.strokeColor().alpha()/255.0, "r": lyr_symbol.strokeColor().red(), "g": lyr_symbol.strokeColor().green(), "b": lyr_symbol.strokeColor().blue() }}
                        styleSttings = {"style": {"type":styleDict[lyr_style_type], "symbol": {"stroke": lyr_symbol_stroke, "fill": lyr_symbol_fill}}}
                    elif lyr_style_type == "categorizedSymbol":
                        cat_field = rend.classAttribute()
                        cat_values = []
                        for c in rend.categories():
                            cat_value = c.value()
                            if type(cat_value) is float:
                                if int(cat_value) == cat_value:
                                    cat_value = str(int(cat_value))
                            cat_alias = c.label()
                            cat_symbol = c.symbol().symbolLayers()[0]
                            lyr_symbol_fill = {"color": {"r": cat_symbol.color().red(),"g":  cat_symbol.color().green(),"b":  cat_symbol.color().blue(),"a":  cat_symbol.color().alpha()/255.0},"type": "solid"}
                            lyr_symbol_stroke =  {"width": cat_symbol.strokeWidth(), "color": { "a": cat_symbol.strokeColor().alpha()/255.0, "r": cat_symbol.strokeColor().red(), "g": cat_symbol.strokeColor().green(), "b": cat_symbol.strokeColor().blue() }}
                            cat_values.append({"type": "Value", "id":str(uuid.uuid4()),"value": f"{cat_value}", "alias": cat_alias, "symbol": {"stroke": lyr_symbol_stroke, "fill": lyr_symbol_fill}})
                        def_type = {"stroke": {"width": 1,"color": {"a": 1,"r": 0,"g": 0,"b": 0}},"fill": {"color": {"a": 1,"r": 134,"g": 155,"b": 228}, "type": "solid"}}
                        styleSttings = {"style": {"type":styleDict[lyr_style_type], "fieldName": cat_field, "symbolValueType": "Value", "values": cat_values, "defaultSymbol": def_type, "removeDefaultFromLegend": True}}
                    elif lyr_style_type ==  "graduatedSymbol":
                        ran_field = rend.classAttribute()
                        ran_values = []
                        for r in rend.ranges():
                            min_value = int(r.lowerValue())
                            max_value = int(r.upperValue())+1
                            ran_alias = r.label()
                            ran_symbol = r.symbol().symbolLayers()[0]
                            lyr_symbol_fill = {"color": {"r": ran_symbol.color().red(),"g":  ran_symbol.color().green(),"b":  ran_symbol.color().blue(),"a":  ran_symbol.color().alpha()/255.0},"type": "solid"}
                            lyr_symbol_stroke =  {"width": ran_symbol.strokeWidth(), "color": { "a": ran_symbol.strokeColor().alpha()/255.0, "r": ran_symbol.strokeColor().red(), "g": ran_symbol.strokeColor().green(), "b": ran_symbol.strokeColor().blue() }}
                            ran_values.append({"type": "Range","id":str(uuid.uuid4()),"minValue": f"{min_value}","maxValue": f"{max_value}", "alias": ran_alias, "symbol": {"stroke": lyr_symbol_stroke, "fill": lyr_symbol_fill}})
                        def_type = {"stroke": {"width": 1,"color": {"a": 1,"r": 0,"g": 0,"b": 0}},"fill": {"color": {"a": 1,"r": 134,"g": 155,"b": 228}, "type": "solid"}}
                        styleSttings = {"style": {"type":styleDict[lyr_style_type], "fieldName": ran_field, "symbolValueType": "Range", "values": ran_values, "defaultSymbol": def_type, "removeDefaultFromLegend": True}}

            req_body = {
                "title": layer_name,
                "tag": layer_tags_string,
                "description": layer_description,
                "data_type": data_type,
                "options": '{}',
                "settings": json.dumps(styleSttings),
                "file": (os.path.basename(self.layerCopyPath_add), open(self.layerCopyPath_add, 'rb'), 'application/octet-stream')
            }

        try:
            req_add_layers = self.api.create_layer(req_body)
            if req_add_layers["code"] == 200:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Слой успешно добавлен")
                msg.setWindowTitle("Статус")
                msg.setStandardButtons(QMessageBox.Ok)
                returnValue = msg.exec()
                self.dlg_add_layer.close()
                self._refresh_click()
                self.dlg_layers.raise_()
                self.dlg_layers.activateWindow()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(str(e))
            msg.setWindowTitle("Ошибка загрузки слоя")
            msg.setStandardButtons(QMessageBox.Ok)
            returnValue = msg.exec()
        if data_type == "gpkg":
            self._clear_folder(self.folderCopyPath_add)
    else:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Необходимо заполнить название слоя")
        msg.setWindowTitle("Статус")
        msg.setStandardButtons(QMessageBox.Ok)
        returnValue = msg.exec()

# add layer button
def _add_click(self):
    self.dlg_add_layer.show()
    if self.dlg_add_layer.map_layers_cb.currentLayer() != None:
        self.dlg_add_layer.add_layer_button.setEnabled(True)
    else:
        self.dlg_add_layer.add_layer_button.setEnabled(False)
    self.dlg_add_layer.map_layers_cb.setFilters(QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PointLayer | QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.RasterLayer)
    try:
        self.dlg_add_layer.map_layers_cb.currentIndexChanged['QString'].disconnect(self._is_raster_lyr)
        self.dlg_add_layer.add_layer_button.clicked.disconnect(self._add_layer)
    except TypeError:
        pass
    self.dlg_add_layer.map_layers_cb.currentIndexChanged['QString'].connect(self._is_raster_lyr)
    self.dlg_add_layer.add_layer_button.clicked.connect(self._add_layer)

