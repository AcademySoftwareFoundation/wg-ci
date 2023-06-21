#include <Partio.h>
#include <iostream>
#include <string>


Partio::ParticlesDataMutable* create_particles()
{
    Partio::ParticlesDataMutable& particle_data = *Partio::create();
    Partio::ParticleAttribute position_attribute = particle_data.addAttribute("position",Partio::VECTOR, 2);
    Partio::ParticleAttribute id_attribute = particle_data.addAttribute("id", Partio::INT,1);
    
    for(int i = 0; i < 10; ++i)
    {
        Partio::ParticleIndex index = particle_data.addParticle();
        float* position = particle_data.dataWrite<float>(position_attribute, index);
        int* id = particle_data.dataWrite<int>(id_attribute, index);

        position[0] = i * 1.f;
        position[1] = i * 2.f;
        id[0] = index;

        std::cout << "id: " << id[0] << " position: [" << position[0] << ", " << position[1] << "]\n";
    }
    return &particle_data;
}

int main(int argc,char *argv[])
{
    auto particle_data = create_particles();
    particle_data->release();

    return 0;

}
