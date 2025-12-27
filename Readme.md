You first need to install nix using this command.
```sh
sudo sh <(curl --proto '=https' --tlsv1.2 -L https://nixos.org/nix/install) --daemon

```
(Official site https://nixos.org/)

Create `/etc/nix/nix.conf` if not exists
Then add `experimental-features = nix-command flakes` to the end.

To run the app use
```sh
nix run github:jitzerttok51/image-datecorrector <list of directories or files>
```
If needed start a new terminal