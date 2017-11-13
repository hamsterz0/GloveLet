//=====================================================================================================
// MadgwickAHRS.h
//=====================================================================================================
//
// Implementation of Madgwick's IMU and AHRS algorithms.
// See: http://www.x-io.co.uk/node/8#open_source_ahrs_and_imu_algorithms
//
// Date			Author          Notes
// 29/09/2011	SOH Madgwick    Initial release
// 02/10/2011	SOH Madgwick	Optimised for reduced CPU load
//
//=====================================================================================================
#ifndef AHRS_COMMON_H_H
#include "../ahrs_common.h"
#endif // AHRS_COMMON_H_H

#ifndef STD_VECTOR_H
#define STD_VECTOR_H
#include <vector>
#endif // STD_VECTOR_H

#ifndef GLM_GTC_QUATERNION_H
#define GLM_GTC_QUATERNION_H
#include <glm/gtc/quaternion.hpp>
#endif // GLM_GTC_QUATERNION_H

#ifndef MadgwickAHRS_h
#define MadgwickAHRS_h

//----------------------------------------------------------------------------------------------------
// Variable declaration

extern volatile float beta;				// algorithm gain
extern volatile float q0, q1, q2, q3;	// quaternion of sensor frame relative to auxiliary frame

//---------------------------------------------------------------------------------------------------
// Function declarations

glm::fquat MadgwickAHRSupdate(float gx, float gy, float gz, float ax, float ay, float az, float mx, float my,
                                      float mz, float sample_freq = sampleFreq);
glm::fquat MadgwickAHRSupdateIMU(float gx, float gy, float gz, float ax, float ay, float az, float sample_freq = sampleFreq);
float invSqrt(float x);

#endif
//=====================================================================================================
// End of file
//=====================================================================================================
