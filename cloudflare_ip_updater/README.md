# hassio-cloudflareipupdater
Dynamic IP Updater for Cloudflare in Home Assistant

[![Community Forum][forum-shield]][forum]


### This Home Assistant Addon

The objective is to provide a client to do dynamic dns updates in Cloudflare on behalf of your hass.io server. The configuration of this addon allows you to setup your Cloudflare domain to dynamically update whenever a change of your public IP address occurs.

### Configuration

The available configuration options are as follows (this is filled in with some example data):

```
{
    "zone": "yourdomain.com",
    "host": "sub.yourdomain.com",
    "email": "hello@yourdomain.com",
    "api": "yourAPIkeyFromCloudflare"
}
```

You should add this in your automations.yaml:

```
- id: cloudflare-updater
  alias: "IP Cloudflare Updater"
  trigger:
  - platform: time_pattern
    # This will match every 1 minutes
    minutes: '/1'
  action:
  - service: hassio.addon_restart
    data:
      addon: local_hassio_cloudflareipupdater
```
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg
[forum]: https://community.home-assistant.io/t/hass-io-addon-dynamic-ip-updater-for-cloudflare/122580
