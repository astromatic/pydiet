// Manage web interface settings
// Copyright CFHT/CNRS/SorbonneU
// Licensed under GPL v3
import {ui_url} from "./url";
import {fetch_html} from "./fetch";
import {prefersdark, toggle_dark_theme} from "./theme";

const settings_button = document.querySelector('#settings-button');

if (settings_button) {
    settings_button.addEventListener('click', async (e) => {
        if (!(await fetch_html('#content-slot', ui_url + "/settings")))
          return false;
        // Manage theme changes
        theme_segment = document.querySelector("#theme-segment");
        theme_segment.addEventListener('ionChange', (event) => {
            isdark = event.detail.value == "dark"
                || (event.detail.value == "auto" && prefersdark.matches); 
            toggle_dark_theme(isdark);
        });
        // Close menu
        document.querySelector("ion-menu").close();
        return true;
    });
}

