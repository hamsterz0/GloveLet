#version 330 core

#ifndef STACK_SZ
#define STACK_SZ 128
#endif // STACK_SZ
layout (location = 0) in vec3 aPos;

out vec4 debugColor;

uniform int model_index = 0;
uniform mat4 model[STACK_SZ];
uniform mat4 projection = mat4(1.0);
uniform mat4 view_lookat = mat4(1.0);
uniform mat4 view = mat4(1.0);

void main() {
  debugColor = vec4(1.0, 1.0, 1.0, 1.0);
  mat4 model_trsfm = mat4(1.0);
  for(int i = model_index; i > -1; i--) {
    model_trsfm = model[i] * model_trsfm;
  }

  mat4 view_trsfm = view * view_lookat;

  gl_Position = projection * view_trsfm * model_trsfm * vec4(aPos, 1.0);
}
