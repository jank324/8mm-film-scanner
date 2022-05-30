# 8mm-film-scanner


/etc/systemd/system

systemctl start 8mmfilmscanner
systemctl status 8mmfilmscanner
journalctl -f
systemctl stop 8mmfilmscanner
systemctl enable 8mmfilmscanner


sudo cp 8mmfilmscanner.service /etc/systemd/system/
