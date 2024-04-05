import { Pane } from "./pane.js";
export class Frame {
    constructor(id, div) {
        this.is_focus = false;
        this.panes = [];
        this.id = id;
        this.div = div;
        this.add_pane = this.add_pane.bind(this);
        this.div.addEventListener('mousedown', this.assign_active_frame.bind(this));
    }
    assign_active_frame() {
        if (!window.active_frame) {
            this.is_focus = true;
            window.active_frame = this;
            window.active_frame.div.classList.add('chart_frame_active');
        }
        else if (window.active_frame.id != this.id) {
            window.active_frame.is_focus = false;
            window.active_frame.div.classList.remove('chart_frame_active');
            this.is_focus = true;
            window.active_frame = this;
            window.active_frame.div.classList.add('chart_frame_active');
        }
    }
    reassign_div(div) {
        this.div = div;
        this.panes.forEach(pane => {
            this.div.appendChild(pane.div);
        });
        this.div.addEventListener('mousedown', this.assign_active_frame.bind(this));
    }
    add_pane(id = '') {
        let child_div = document.createElement('div');
        child_div.classList.add('chart_pane');
        this.div.appendChild(child_div);
        let new_pane = new Pane(id, child_div);
        this.panes.push(new_pane);
        this.resize();
        return new_pane;
    }
    resize() {
        let this_width = this.div.clientWidth;
        let this_height = this.div.clientHeight;
        this.panes.forEach(pane => {
            pane.resize(this_width, this_height);
        });
    }
    fitcontent() {
        this.panes.forEach(pane => {
            pane.fitcontent();
        });
    }
}
