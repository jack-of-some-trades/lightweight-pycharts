//Typescript API that interfaces with python.

import { icon_manager } from "./icons.js";
import { Container_Layouts, Series_Type, symbol_item } from "./util.js";


//Each Function Maps directly to a function within the js_api class in js_api.py
export class py_api {
    loaded!: () => void;
    close!: () => void;
    maximize!: () => void;
    minimize!: () => void;
    restore!: () => void;

    add_container!: () => void;
    remove_container!: (id: string) => void;
    reorder_containers!: (from: number, to: number) => null

    layout_change!: (container_id: string, layout: Container_Layouts) => void;
    series_change!: (container_id: string, frame_id: string, series_type: Series_Type) => void
    data_request!: (container_id: string, frame_id: string, symbol: symbol_item, mult: number, period: string) => void;
    symbol_search!: (symbol: string, types: string[], brokers: string[], exchanges: string[], confirmed: boolean) => void;

    callback!: (msg: string) => void;
    constructor() { this._loaded_check = this._loaded_check.bind(this) }

    //The Python "View" Subclasses Kick starts this recursive check 
    //immediately after they assigns the api callbacks above
    //=> those are guaranteed to have been loaded.
    _loaded_check() {
        //Check that everything outside of this class has been loaded
        if (icon_manager.loaded && window.loaded) {
            //Once everything is loaded break recursion and make the python callback
            //this.loaded() should only be called once and called from here
            this.loaded()
            //Window Size is very small when hidden, need to resize once it's visible
            setTimeout(window.wrapper.resize.bind(window.wrapper), 200)
        } else {
            setTimeout(this._loaded_check, 50)
        }
    }
}