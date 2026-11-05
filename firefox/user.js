// Maria Padilha Firefox preferences.
//
// padilha-dots copies this file into the detected default profile. It is a
// normal copy, not a symlink, because Firefox and profile managers expect a
// regular user.js at the profile root; the chrome CSS next to it is linked.
//
// Keep this file minimal. Everything else belongs in the Firefox UI, in
// prefs.js, or in the CSS under chrome/.

// Load chrome/userChrome.css (browser UI) and chrome/userContent.css (new tab,
// about:blank, private browsing) from the profile. Without this pref Firefox
// ignores both files, including the chrome/lilith.css palette they import.
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);
