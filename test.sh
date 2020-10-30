#!/bin/sh

cat <<EOF
<!DOCTYPE html>
<html>
  <head>
  </head>
  <body>
  <material-paper>
      <rainbow-text><p>Henlo</p></rainbow-text>
      <lucky-number></lucky-number><br>
      <green-button href="https://www.piworks.net/" target="_blank">Go to P.I. Works</green-button>
  </material-paper>
  <script>$(./compile.py components/*)</script>
  </body>
</html>
EOF
