# Terminalizer

```
rm -rf /tmp/aws-auto-inventory-report
rm -f /tmp/aws-auto-inventory*
cp dist/aws-auto-inventory /tmp/aws-auto-inventory-darwin-amd64
terminalizer record run --config clencli/terminalizer.yml --skip-sharing
cat ~/.config/aws-auto-inventory/config.yaml
./aws-auto-inventory-darwin-amd64 --name learning &
ls -ltha aws-auto-inventory-report/log.txt
tail -f aws-auto-inventory-report/log.txt
ls -ltha aws-auto-inventory-report/*.xlsx
terminalizer render run --output clencli/terminalizer/run.gif
```