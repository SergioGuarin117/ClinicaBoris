import { Shield, Clock, Users, Star } from 'lucide-react';
import { ImageWithFallback } from './figma/ImageWithFallback';

export function WhyChooseUs() {
  const reasons = [
    {
      icon: Shield,
      title: 'Tecnología de Vanguardia',
      description: 'Equipamiento médico de última generación para procedimientos más seguros y efectivos.',
    },
    {
      icon: Clock,
      title: 'Atención Personalizada',
      description: 'Seguimiento continuo antes, durante y después de cada procedimiento quirúrgico.',
    },
    {
      icon: Users,
      title: 'Equipo Multidisciplinario',
      description: 'Trabajo en conjunto con especialistas para una atención integral y completa.',
    },
    {
      icon: Star,
      title: 'Experiencia Comprobada',
      description: 'Miles de cirugías exitosas con los más altos estándares de calidad y seguridad.',
    },
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl mb-4 text-gray-900">¿Por Qué Elegirnos?</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Comprometidos con tu salud y bienestar en cada etapa del proceso
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-12 items-center mb-12">
          <div className="rounded-2xl overflow-hidden shadow-xl">
            <ImageWithFallback
              src="https://images.unsplash.com/photo-1762625570087-6d98fca29531?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBtZWRpY2FsJTIwY2xpbmljJTIwaW50ZXJpb3J8ZW58MXx8fHwxNzcxMDY1MTYxfDA&ixlib=rb-4.1.0&q=80&w=1080"
              alt="Instalaciones médicas modernas"
              className="w-full h-auto"
            />
          </div>
          <div className="space-y-6">
            {reasons.map((reason, index) => {
              const Icon = reason.icon;
              return (
                <div key={index} className="flex gap-4">
                  <div className="flex-shrink-0">
                    <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center">
                      <Icon className="w-6 h-6 text-blue-600" />
                    </div>
                  </div>
                  <div>
                    <h3 className="text-xl mb-2 text-gray-900">{reason.title}</h3>
                    <p className="text-gray-600">{reason.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
