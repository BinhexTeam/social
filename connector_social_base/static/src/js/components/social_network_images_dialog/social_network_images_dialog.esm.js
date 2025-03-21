/** @odoo-module **/

import {Component, useRef, useState} from "@odoo/owl";
import {Dialog} from "@web/core/dialog/dialog";

export class SocialNetworkImagesDialog extends Component {
    static template = "connector_social_base.SocialNetworkImagesDialog";
    static components = {
        Dialog,
    };

    setup() {
        super.setup();
        this.carouselRef = useRef("carouselRef");
        this.state = useState({
            imageUrlActive: this.props.images[0],
        });
    }

    indexImageActive(prev = false, next = false) {
        let current_index = this.props.images.indexOf(this.state.imageUrlActive);
        if (prev) {
            current_index = (current_index === 0 ? 2 : current_index) - 1;
        } else if (next) {
            current_index = (current_index + 1) % this.props.images.length;
        }
        return this.props.images[current_index];
    }

    prevImage() {
        this.state.imageUrlActive = this.indexImageActive(true);
    }

    nextImage() {
        this.state.imageUrlActive = this.indexImageActive(false, true);
    }
}
