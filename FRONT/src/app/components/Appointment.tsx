import { Calendar, Clock, CheckCircle2 } from 'lucide-react';

export function Appointment() {
  const plans = [
    {
      title: 'Consulta Estándar',
      price: '300',
      duration: '30 minutos',
      features: [
        'Evaluación médica completa',
        'Revisión de estudios previos',
        'Diagnóstico profesional',
        'Plan de tratamiento inicial',
      ],
    },
    {
      title: 'Consulta Premium',
      price: '600',
      duration: '60 minutos',
      features: [
        'Todo lo incluido en consulta estándar',
        'Tiempo extendido de consulta',
        'Segunda opinión detallada',
        'Análisis exhaustivo de opciones',
        'Plan de seguimiento personalizado',
      ],
      popular: true,
    },
  ];

  const handleAppointment = (price: string) => {
    // Aquí iría la lógica para procesar el pago o reserva
    alert(`Has seleccionado la consulta de $${price} USD. En breve serás redirigido al sistema de pago.`);
  };

  return (
    <section id="separar-cita" className="py-20 bg-gradient-to-br from-blue-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl mb-4 text-gray-900">Separa tu Cita</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Elige el tipo de consulta que mejor se adapte a tus necesidades
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`relative bg-white rounded-2xl shadow-xl p-8 ${
                plan.popular ? 'border-2 border-blue-600 transform md:scale-105' : ''
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm">
                    Más Popular
                  </span>
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="text-2xl mb-2 text-gray-900">{plan.title}</h3>
                <div className="flex items-center justify-center gap-2 text-gray-600 mb-4">
                  <Clock className="w-5 h-5" />
                  <span>{plan.duration}</span>
                </div>
                <div className="flex items-baseline justify-center gap-2">
                  <span className="text-5xl text-blue-600">${plan.price}</span>
                  <span className="text-gray-500">USD</span>
                </div>
              </div>

              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleAppointment(plan.price)}
                className={`w-full py-4 rounded-lg transition flex items-center justify-center gap-2 ${
                  plan.popular
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-100 text-blue-600 hover:bg-gray-200 border-2 border-blue-600'
                }`}
              >
                <Calendar className="w-5 h-5" />
                Separar Consulta
              </button>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <p className="text-gray-600 mb-4">
            ¿Necesitas más información? Contáctanos directamente
          </p>
          <a
            href="#contacto"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 transition"
          >
            Ver información de contacto →
          </a>
        </div>
      </div>
    </section>
  );
}
