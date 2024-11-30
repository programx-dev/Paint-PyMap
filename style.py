style_sheet = """
#widget {
    background-color: #f9f9f9;
}

#canvas {
    border: 0px;
}

#tool_button[state="normal"] {
    border-radius: 7px;
    background-color: #f9f9f9;
    border-style: flat;
    border-width: 1px;
} 

#tool_button[state="selected"] {
    margin: 1px;
    background-color: #f3f3f3;
    border-radius: 7px;
    border-style: solid;
    border-color: #003e92;
    border-width: 1px;
}

#primary_color_button {
    border-style: solid;
    border-color: #003e92;
    border-width: 1px;
    border-radius: 16;
    margin: 1px;
}

#palette_button {
    border-width: 1px;
    border-radius: 11px;
    border-style: solid;
    padding: 1px;
    border-color: #bababa;
}

#separator {
    background: #eaeaea;
    border: 0px;
}

#size_combobox {
    color: #666666;
    font-size: 14px;
    padding: 1px 15px 1px 3px;
    border: 1px solid #e4e4e4;
    border-radius: 5px;
}

#size_combobox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 10px;
    padding: 4px;
    border: none;
    image: url(./icons/arrow_down.png);
}

#size_combobox QAbstractItemView {
    outline: 0;
    border-radius: 10px;
    background: white;
    border: 1px solid gray;
    padding: 4px 4px 4px 4px
}

#size_combobox QAbstractItemView::item:selected {
    border-radius: 4px;
    background: #e3e1e3;
    color: #000000
}    
"""