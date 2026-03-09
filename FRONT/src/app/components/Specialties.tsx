import { Activity, Scissors, Heart, Stethoscope, UserCheck, Zap } from 'lucide-react';

export function Specialties() {
  const specialties = [
    {
      icon: Scissors,
      title: 'Cirugía Laparoscópica',
      description: 'Procedimientos mínimamente invasivos para una recuperación más rápida y menos dolor postoperatorio.',
    },
    {
      icon: Activity,
      title: 'Cirugía General',
      description: 'Tratamiento de hernias, vesícula biliar, apendicitis y otras condiciones abdominales.',
    },
    {
      icon: Heart,
      title: 'Cirugía Bariátrica',
      description: 'Procedimientos especializados para el tratamiento de obesidad y mejora de la calidad de vida.',
    },
    {
      icon: Stethoscope,
      title: 'Cirugía de Tiroides',
      description: 'Tratamiento quirúrgico de nódulos tiroideos, bocio y cáncer de tiroides.',
    },
    {
      icon: UserCheck,
      title: 'Cirugía Oncológica',
      description: 'Tratamiento quirúrgico especializado de tumores con enfoque multidisciplinario.',
    },
    {
      icon: Zap,
      title: 'Cirugía de Emergencia',
      description: 'Atención inmediata y especializada para procedimientos urgentes las 24 horas.',
    },
  ];

  return (
    <section id="especialidades" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl mb-4 text-gray-900">Especialidades Médicas</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Ofrecemos una amplia gama de servicios quirúrgicos con tecnología de última generación
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {specialties.map((specialty, index) => {
            const Icon = specialty.icon;
            return (
              <div 
                key={index} 
                className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow"
              >
                <div className="bg-blue-100 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                  <Icon className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-xl mb-3 text-gray-900">{specialty.title}</h3>
                <p className="text-gray-600">{specialty.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
