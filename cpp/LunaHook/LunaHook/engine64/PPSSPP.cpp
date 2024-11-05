#include "PPSSPP.h"
#include "ppsspp/psputils.hpp"

bool PPSSPPengine::attach_function()
{
	return InsertPPSSPPcommonhooks();
}
