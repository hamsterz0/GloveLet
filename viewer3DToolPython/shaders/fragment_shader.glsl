#version 330 core
in vec4 debugColor;
out vec4 fragColor;

uniform bool useColor = true;
uniform vec4 color = {1.0, 1.0, 1.0, 1.0};

void main() {
  if(useColor) fragColor = color;
  else fragColor = debugColor;
}
