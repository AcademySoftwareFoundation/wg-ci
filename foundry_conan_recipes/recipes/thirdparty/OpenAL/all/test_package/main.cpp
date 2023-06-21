#include <AL/al.h>
#include <AL/alc.h>

int main() {
    // Default to "success" as there may be no audio devices.
    int result = 0;

    ALCdevice* device = alcOpenDevice(nullptr);
    if (device)
    {
        ALCcontext* context = alcCreateContext(device, nullptr);
        if (context)
        {
            if (alcMakeContextCurrent(context) == ALC_TRUE)
            {
                ALenum error = alGetError();
                if (error != AL_NO_ERROR)
                {
                    result = 1;
                }
            }

            alcDestroyContext(context);
            context = nullptr;
        }

        alcCloseDevice(device);
        device = nullptr;
    }

    return result;
}
