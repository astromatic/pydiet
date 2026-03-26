// Javascript code entry point
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under MIT
import {get_instruments} from "./instrument"
import {setup_instrument_settings, setup_theme_settings} from "./settings";

// Set up theme section of settings
setup_theme_settings();

get_instruments().then( (instruments) => {
// Set up instrument section of settings
	setup_instrument_settings(instruments);
});


