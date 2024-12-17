// Javascript code entry point
// Copyright CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under MIT
import {get_instruments} from "./instrument"
import {setup_instrument_settings, setup_theme_settings} from "./settings";
import {update_filters} from "./etc";

// Set up theme section of settings
setup_theme_settings();
get_instruments().then( (instruments) => {
// Set up instrument section of settings
	setup_instrument_settings(instruments);
});


