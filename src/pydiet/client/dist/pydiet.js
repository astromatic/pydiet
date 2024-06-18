(() => {
  // js/theme.js
  var prefersdark = window.matchMedia("(prefers-color-scheme: dark)");
  function toggle_dark_theme(isdark2) {
    document.body.classList.toggle("dark", isdark2);
  }

  // js/url.js
  var root_path = document.querySelector("#root_path").content;
  var ui_url = root_path + "/ui";
  var ui_auth_url = ui_url + "/auth";

  // js/fetch.js
  async function fetch_html(selector, url) {
    return await fetch(url, { credentials: "include" }).then((response) => {
      if (!response.ok)
        throw new Error("Unauthorized API endpoint:" + response.url);
      return response.text();
    }).then((html) => {
      parent = document.querySelector(selector);
      if (parent.firstElementChild)
        parent.firstElementChild.remove();
      parent.insertAdjacentHTML("beforeend", html);
      return true;
    }).catch((err) => {
      return false;
    });
  }

  // js/settings.js
  var settings_button = document.querySelector("#settings-button");
  if (settings_button) {
    settings_button.addEventListener("click", async (e) => {
      if (!await fetch_html("#content-slot", ui_url + "/settings"))
        return false;
      theme_segment = document.querySelector("#theme-segment");
      theme_segment.addEventListener("ionChange", (event) => {
        isdark = event.detail.value == "dark" || event.detail.value == "auto" && prefersdark.matches;
        toggle_dark_theme(isdark);
      });
      document.querySelector("ion-menu").close();
      return true;
    });
  }

  // js/main.js
  toggle_dark_theme(prefersdark.matches);
})();
