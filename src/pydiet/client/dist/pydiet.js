(() => {
  // js/theme.js
  var themes = ["Light", "Dark", "Auto"];
  var theme_icons = ["sunny", "moon", "contrast"];
  var prefersdark = window.matchMedia("(prefers-color-scheme: dark)");
  function toggle_dark_theme(isdark) {
    document.body.classList.toggle("dark", isdark);
  }
  function get_theme() {
    return localStorage.getItem("pyDIETDefaultTheme");
  }
  function update_theme(theme) {
    if (theme) {
      localStorage.setItem("pyDIETDefaultTheme", theme);
    } else {
      theme = get_theme();
    }
    toggle_dark_theme(
      typeof theme === "string" && theme.includes("dark") || !(typeof theme === "string" && theme.includes("light")) && prefersdark.matches
    );
  }

  // js/url.js
  var root_path = document.querySelector("#root_path").content;
  var root_url = root_path;
  var etc_url = root_url + "/etc";
  var ui_url = root_url + "/ui";
  var ui_auth_url = ui_url + "/auth";

  // js/etc.js
  var etc_form = document.querySelector("#etc-form");
  etc_form.addEventListener("submit", async function(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(this));
    fetch(etc_url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    }).then(async (response) => {
      const json = response.json();
      const status = response.status;
      if (status == 201) {
        return await fetch_signin() ? true : false;
      } else if (response.status == 400)
        alert("Unprocessable ETC query.");
      else if ("reason" in json)
        alert(`ETC query failed: ${json.reason}`);
      else
        alert("Unknown error.");
    }).catch((error) => {
      alert("Communication error during ETC query.");
    });
  });

  // js/camera.js
  var cameras = ["MegaCam", "WIRCam"];
  function get_camera() {
    return localStorage.getItem("pyDIETDefaultCamera");
  }
  function update_camera(camera) {
    if (camera) {
      localStorage.setItem("pyDIETDefaultCamera", camera);
    } else {
      camera = get_camera();
    }
  }

  // js/settings.js
  if (theme_segment = document.querySelector("#theme-segment")) {
    for (t in themes) {
      let button = document.createElement("ion-segment-button"), icon = document.createElement("ion-icon"), label = document.createElement("ion-label");
      button.value = themes[t].toLowerCase();
      label.innerHTML = themes[t];
      button.appendChild(label);
      icon.name = theme_icons[t];
      button.appendChild(icon);
      theme_segment.appendChild(button);
    }
    theme_segment.value = get_theme();
    theme_segment.addEventListener("ionChange", (event) => {
      update_theme(event.detail.value);
    });
  }
  if (camera_segment = document.querySelector("#camera-segment")) {
    for (c in cameras) {
      let button = document.createElement("ion-segment-button"), icon = document.createElement("ion-icon"), label = document.createElement("ion-label");
      button.value = cameras[c].toLowerCase();
      label.innerHTML = cameras[c];
      button.appendChild(label);
      icon.name = "videocam";
      button.appendChild(icon);
      camera_segment.appendChild(button);
    }
    camera_segment.value = get_camera();
    camera_segment.addEventListener("ionChange", (event) => {
      update_camera(event.detail.value);
    });
  }

  // js/main.js
  update_theme();
})();
