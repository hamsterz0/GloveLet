//
// Created by joseph on 11/2/17.
//
#pragma once

#include "WorldObject.h"

using namespace glm;

WorldObject::~WorldObject() {
    if(parent) {
        if(prev_sibling) {
            prev_sibling->next_sibling = next_sibling;
            next_sibling->prev_sibling = prev_sibling;
        } else if(next_sibling) {
            next_sibling->prev_sibling = nullptr;
        }
    }

    if(first_child) {
        WorldObject* next = first_child;
        while(next != nullptr) {
            next->parent = this->parent;
            next->next_sibling;
        }
    }
}

WorldObject::WorldObject() {
    world_pos = fvec3(0.0f, 0.0f, 0.0f);
    local_pos = fvec3(world_pos);
    world_quat = fquat(1.0f, 0.0f, 0.0f, 0.0f);
    local_quat = fquat(world_quat);
    polygons = nullptr;
}

