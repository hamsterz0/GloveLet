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
// TODO doc
WorldObject::WorldObject() {
    world_pos = fvec3(0.0f, 0.0f, 0.0f);
    local_pos = fvec3(world_pos);
    world_quat = fquat(1.0f, 0.0f, 0.0f, 0.0f);
    local_quat = fquat(world_quat);
    polygons = nullptr;
}
// TODO doc
WorldObject::WorldObject(glm::fvec3 &position) {
    world_pos = fvec3(position);
    local_pos = fvec3(world_pos);
    world_quat = fquat(1.0f, 0.0f, 0.0f, 0.0f);
    local_quat = fquat(world_quat);
    polygons = nullptr;
}
// TODO doc
WorldObject::WorldObject(fvec3 &position, fvec3 &euler_angles) {
    world_pos = fvec3(position);
    local_pos = fvec3(world_pos);
    world_quat = fquat(euler_angles);
    local_quat = fquat(world_quat);
    polygons = nullptr;
}
// TODO doc
WorldObject::WorldObject(fvec3 &position, fquat &quaternion) {
    world_pos = fvec3(position);
    local_pos = fvec3(world_pos);
    world_quat = fquat(quaternion);
    local_quat = fquat(world_quat);
    polygons = nullptr;
}
/*!
 * Moves the \c WorldObject by the amount in \p ds.
 * @param ds - the delta-position vector
 */
void WorldObject::move(glm::fvec3 &ds) {
    world_pos += ds;
}
// TODO doc
void WorldObject::detachChild(WorldObject &child) {
    // TODO define
}
// TODO doc
void WorldObject::addChild(WorldObject &child) {
    // TODO define
}
// TODO doc
void WorldObject::setParent(WorldObject &parent) {
    // TODO define
}
// TODO doc
void WorldObject::updateQuaternion(glm::fvec3 &euler_angles) {
    // TODO define
}
// TODO doc
glm::fvec3 WorldObject::getWorldPosition() {
    // TODO define
}
// TODO doc
void WorldObject::setWorldPosition(glm::fvec3 &pos) {
    // TODO define
}
// TODO doc
glm::fvec3 WorldObject::getLocalPosition() {
    // TODO define
}
// TODO doc
void WorldObject::setLocalPosition(glm::fvec3 &pos) {
    // TODO define
}

glm::fquat WorldObject::getWorldRotation() {
    // TODO define
}

void WorldObject::setWorldRotation(glm::fquat &rot) {
    // TODO define
}

glm::fquat WorldObject::getLocalRotation() {
    // TODO define
}

void WorldObject::setLocalRotation(glm::fquat &rot) {
    // TODO define
}

WorldObject *WorldObject::getPrevSibling() {
    // TODO define
}

void WorldObject::setPrevSibling(WorldObject &wo) {
    // TODO define
}

WorldObject *WorldObject::getNextSibling() {
    // TODO define
}

void WorldObject::setNextSibling(WorldObject &wo) {
    // TODO define
}

