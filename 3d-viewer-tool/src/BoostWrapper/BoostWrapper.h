//
// Created by joseph on 12/14/17.
//

#ifndef GLM_GLM_H
#define GLM_GLM_H
#include <glm/glm.hpp>
#endif //GLM_GLM_H

#ifndef TEMPLATE_OBJECTS_H
#include "../Template Objects/TemplateObjects.h"
#endif // TEMPLATE_OBJECTS_H

#ifndef BOOST_PYTHON_H
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
#endif

#ifndef BOOSTWRAPPER_H
#define BOOSTWRAPPER_H

namespace np = boost::python::numpy;
namespace py = boost::python;

namespace py3deeViewer {
    class WorldObjectWrapper {
    private:
        WorldObject wo;
    public:
        ~WorldObjectWrapper();
        WorldObjectWrapper();
        WorldObjectWrapper(MeshWrapper &mesh, np::ndarray const &position);
        WorldObjectWrapper(MeshWrapper &mesh, np::ndarray const &position, np::ndarray const &rotation);
    };

    /*!
     * @brief Boost.Python wrapper for glm::fvec3 data structure.
     */
    class FVec3Wrapper {
    private:
        glm::fvec3 vec = glm::gfvec3(0.0f, 0.0f, 0.0f);
    public:
        FVec3Wrapper(float x, float y, float z);
    };
}

#endif //BOOSTWRAPPER_H
