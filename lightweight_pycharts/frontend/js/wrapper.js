import { Container } from "./container.js";
import * as u from "./util.js";
import { Wrapper_Divs } from "./util.js";
export class Wrapper {
    constructor() {
        this.loaded = false;
        this.containers = [];
        this.resizeTimeoutID = null;
        this.div = document.createElement('div');
        this.div.id = 'layout_wrapper';
        this.div.classList.add('wrapper');
        document.body.appendChild(this.div);
        this.div_title = document.createElement('div');
        this.div_title.id = 'layout_title';
        this.div_title.classList.add('layout_title', 'layout_flex');
        this.div_title.style.height = `${u.LAYOUT_DIM_TITLE.HEIGHT}px`;
        this.div_title.style.width = u.LAYOUT_DIM_TITLE.WIDTH;
        this.div_title.style.left = `${u.LAYOUT_DIM_TITLE.LEFT}px`;
        this.div_title.style.top = `${u.LAYOUT_DIM_TITLE.TOP}px`;
        this.div_title.style.display = 'flex';
        this.div.appendChild(this.div_title);
        this.div_top = document.createElement('div');
        this.div_top.id = 'layout_top';
        this.div_top.classList.add('layout_main', 'layout_flex');
        this.div_top.style.height = `${u.LAYOUT_DIM_TOP.HEIGHT}px`;
        this.div_top.style.width = u.LAYOUT_DIM_TOP.WIDTH;
        this.div_top.style.left = `${u.LAYOUT_DIM_TOP.LEFT}px`;
        this.div_top.style.top = `${u.LAYOUT_DIM_TOP.TOP}px`;
        this.div_top.style.display = 'flex';
        this.div.appendChild(this.div_top);
        this.div_left = document.createElement('div');
        this.div_left.id = 'layout_left';
        this.div_left.classList.add('layout_main', 'layout_flex');
        this.div_left.style.height = `${u.LAYOUT_DIM_LEFT.HEIGHT}px`;
        this.div_left.style.width = `${u.LAYOUT_DIM_LEFT.WIDTH}px`;
        this.div_left.style.left = `${u.LAYOUT_DIM_LEFT.LEFT}px`;
        this.div_left.style.top = `${u.LAYOUT_DIM_LEFT.TOP}px`;
        this.div_left.style.display = 'flex';
        this.div.appendChild(this.div_left);
        this.div_right = document.createElement('div');
        this.div_right.id = 'layout_right';
        this.div_right.classList.add('layout_main', 'layout_flex');
        this.div_right.style.height = `${u.LAYOUT_DIM_RIGHT.HEIGHT}px`;
        this.div_right.style.width = `${u.LAYOUT_DIM_RIGHT.WIDTH}px`;
        this.div_right.style.right = `${u.LAYOUT_DIM_RIGHT.RIGHT}px`;
        this.div_right.style.top = `${u.LAYOUT_DIM_RIGHT.TOP}px`;
        this.div_right.style.display = 'flex';
        this.div.appendChild(this.div_right);
        this.div_bottom = document.createElement('div');
        this.div_bottom.id = 'layout_bottom';
        this.div_bottom.classList.add('layout_main');
        this.div_bottom.style.height = `${u.LAYOUT_DIM_BOTTOM.HEIGHT}px`;
        this.div_bottom.style.width = `${u.LAYOUT_DIM_BOTTOM.WIDTH}px`;
        this.div_bottom.style.left = `${u.LAYOUT_DIM_BOTTOM.LEFT}px`;
        this.div_bottom.style.bottom = `${u.LAYOUT_DIM_BOTTOM.BOTTOM}px`;
        this.div_bottom.style.display = 'flex';
        this.div.appendChild(this.div_bottom);
        this.div_center = document.createElement('div');
        this.div_center.id = 'layout_center';
        this.div_center.classList.add('layout_main');
        this.div_center.style.height = `${u.LAYOUT_DIM_CENTER.HEIGHT}px`;
        this.div_center.style.width = `${u.LAYOUT_DIM_CENTER.WIDTH}px`;
        this.div_center.style.left = `${u.LAYOUT_DIM_CENTER.LEFT}px`;
        this.div_center.style.top = `${u.LAYOUT_DIM_CENTER.TOP}px`;
        this.div_center.style.display = 'flex';
        this.div.appendChild(this.div_center);
        this.resize();
        window.addEventListener('resize', this.resize.bind(this));
        this.loaded = true;
    }
    resize() {
        let width = window.innerWidth;
        let height = window.innerHeight;
        this.div.style.width = `${width}px`;
        this.div.style.height = `${height}px`;
        let side_bar_height = height;
        let center_height = height - u.LAYOUT_DIM_TITLE.HEIGHT;
        let center_width = width;
        if (this.div_top.style.display === 'flex') {
            side_bar_height -= (u.LAYOUT_DIM_TOP.HEIGHT + u.LAYOUT_MARGIN);
            center_height -= (u.LAYOUT_DIM_TOP.HEIGHT + u.LAYOUT_MARGIN);
        }
        if (this.div_left.style.display === 'flex') {
            center_width -= (u.LAYOUT_DIM_LEFT.WIDTH + u.LAYOUT_MARGIN);
        }
        if (this.div_right.style.display === 'flex') {
            center_width -= (u.LAYOUT_DIM_RIGHT.WIDTH + u.LAYOUT_MARGIN);
        }
        if (this.div_bottom.style.display === 'flex') {
            center_height -= (u.LAYOUT_DIM_BOTTOM.HEIGHT + u.LAYOUT_MARGIN);
        }
        this.div_left.style.height = `${side_bar_height}px`;
        this.div_right.style.height = `${side_bar_height}px`;
        this.div_center.style.height = `${center_height}px`;
        this.div_center.style.width = `${center_width}px`;
        this.div_bottom.style.width = `${center_width}px`;
        if (window.active_container) {
            window.active_container.resize();
        }
    }
    get_div(section) {
        switch (section) {
            case (Wrapper_Divs.TITLE_BAR): return this.div_title;
            case (Wrapper_Divs.CHART): return this.div_center;
            case (Wrapper_Divs.DRAW_TOOLS): return this.div_left;
            case (Wrapper_Divs.NAV_BAR): return this.div_right;
            case (Wrapper_Divs.TOP_BAR): return this.div_top;
            case (Wrapper_Divs.UTIL_BAR): return this.div_bottom;
            default: return this.div;
        }
    }
    show_section(div_loc) {
        switch (div_loc) {
            case (Wrapper_Divs.DRAW_TOOLS):
                this.div_left.style.display = 'flex';
                this.div_center.style.left = `${u.LAYOUT_DIM_CENTER.LEFT}px`;
                this.div_bottom.style.left = `${u.LAYOUT_DIM_BOTTOM.LEFT}px`;
                break;
            case (Wrapper_Divs.NAV_BAR):
                this.div_right.style.display = 'flex';
                break;
            case (Wrapper_Divs.TOP_BAR):
                this.div_top.style.display = 'flex';
                this.div_left.style.top = `${u.LAYOUT_DIM_LEFT.TOP}px`;
                this.div_right.style.top = `${u.LAYOUT_DIM_RIGHT.TOP}px`;
                this.div_center.style.top = `${u.LAYOUT_DIM_CENTER.TOP}px`;
                break;
            case (Wrapper_Divs.UTIL_BAR):
                this.div_bottom.style.display = 'flex';
        }
        this.resize();
    }
    hide_section(section) {
        switch (section) {
            case (Wrapper_Divs.DRAW_TOOLS):
                this.div_left.style.display = 'none';
                this.div_center.style.left = '0px';
                this.div_bottom.style.left = '0px';
                break;
            case (Wrapper_Divs.NAV_BAR):
                this.div_right.style.display = 'none';
                break;
            case (Wrapper_Divs.TOP_BAR):
                this.div_top.style.display = 'none';
                this.div_left.style.top = `${u.LAYOUT_DIM_TITLE.HEIGHT}px`;
                this.div_right.style.top = `${u.LAYOUT_DIM_TITLE.HEIGHT}px`;
                this.div_center.style.top = `${u.LAYOUT_DIM_TITLE.HEIGHT}px`;
                break;
            case (Wrapper_Divs.UTIL_BAR):
                this.div_bottom.style.display = 'none';
        }
        this.resize();
    }
    reorder_containers(from, to) {
        if (from < 0 || from >= this.containers.length)
            console.error(`Index, 'from=${from}', out of bounds on container reorder call. list len = ${this.containers.length}`);
        else if (to < 0 || to >= this.containers.length)
            console.error(`Index, 'to=${to}', out of bounds on container reorder call. list len = ${this.containers.length}`);
        else {
            this.containers.splice(to, 0, this.containers.splice(from, 1)[0]);
            let id_list = [];
            this.containers.forEach(container => { id_list.push(container.id); });
        }
    }
    add_container(id) {
        let tmp_ref = new Container(this.div_center, id);
        this.containers.push(tmp_ref);
        return tmp_ref;
    }
    remove_container(id) {
        for (let i = 0; i < this.containers.length; i++) {
            if (this.containers[i].id === id) {
                let objs = this.containers.splice(i, 1);
                objs[0].remove();
                return;
            }
        }
    }
    set_active_container(tab_div) {
        for (let i = 0; i < this.containers.length; i++) {
            if (this.containers[i].tab_div == tab_div) {
                this.containers[i].assign_active_container();
                break;
            }
        }
    }
    resize_debounce() {
        if (this.resizeTimeoutID !== null) {
            clearTimeout(this.resizeTimeoutID);
            this.resizeTimeoutID = null;
            this.resize();
        }
        else {
            this.resizeTimeoutID = setTimeout(this.resize_debounce, 20);
        }
    }
}
