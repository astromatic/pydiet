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

  // js/fetch.js
  async function fetch_html(selector, url) {
    return await fetch(url, { credentials: "include" }).then((response) => {
      if (!response.ok) {
        throw new Error("Unauthorized API endpoint:" + response.url);
      }
      return response.text();
    }).then((html) => {
      parent = document.querySelector(selector);
      if (parent.firstElementChild) {
        parent.firstElementChild.remove();
      }
      parent.insertAdjacentHTML("beforeend", html);
      return true;
    }).catch((err) => {
      return false;
    });
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
    fetch_html(
      "#modal-slot",
      etc_url + "/" + get_camera() + "?" + new URLSearchParams(data)
    );
  });

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
