#version 130
in vec4 debugColor;
out vec4 fragColor;

uniform bool useColor = true;
uniform vec4 color = vec4(1.0, 1.0, 1.0, 1.0);

void main() {
  if(useColor) fragColor = color;
  else fragColor = debugColor;
}
