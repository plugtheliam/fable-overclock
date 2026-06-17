Output assets/demo-2x.gif

Set Shell zsh
Set FontSize 17
Set Width 1280
Set Height 500
Set Theme "Catppuccin Mocha"
Set Padding 24
Set TypingSpeed 16ms
Set PlaybackSpeed 2.0

Hide
Type "setopt interactive_comments; clear" Enter
Show

Sleep 400ms
Type "# fable-overclock: flag claims with no source before they ship"
Enter
Sleep 600ms

Type `echo 'Revenue grew 38% and added 14,000 users.' | python3 harness/gate/refuse.py`
Enter
Sleep 2200ms

Type "# add the source the gate asked for:"
Enter
Sleep 400ms

Type `echo 'Revenue grew 38% (Stripe, 2026-06-15), 14,000 users (Mixpanel, 2026-06-15).' | python3 harness/gate/refuse.py`
Enter
Sleep 2200ms
