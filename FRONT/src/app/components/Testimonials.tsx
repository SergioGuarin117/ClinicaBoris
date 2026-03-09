import { Star, Quote } from 'lucide-react';
import { ImageWithFallback } from './figma/ImageWithFallback';

export function Testimonials() {
  const testimonials = [
    {
      name: 'María González',
      procedure: 'Cirugía Laparoscópica',
      rating: 5,
      text: 'El Dr. Méndez es un excelente profesional. Me sentí en las mejores manos durante todo el proceso. Su equipo es muy atento y las instalaciones son de primera.',
      image: 'https://images.unsplash.com/photo-1592206934769-67dc0e88b5e3?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoaXNwYW5pYyUyMHdvbWFuJTIwcHJvZmVzc2lvbmFsJTIwcG9ydHJhaXR8ZW58MXx8fHwxNzcxMDc5ODQ2fDA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      name: 'Roberto Sánchez',
      procedure: 'Cirugía Bariátrica',
      rating: 5,
      text: 'Después de años luchando con mi peso, el Dr. Méndez me dio una nueva oportunidad de vida. El seguimiento postoperatorio ha sido excepcional.',
      image: 'https://images.unsplash.com/photo-1617746652974-0be48cd984d1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoaXNwYW5pYyUyMG1hbiUyMHByb2Zlc3Npb25hbCUyMHBvcnRyYWl0fGVufDF8fHx8MTc3MTAxODU1OXww&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      name: 'Ana Martínez',
      procedure: 'Cirugía de Tiroides',
      rating: 5,
      text: 'Profesionalismo y calidez humana. El doctor explicó todo el procedimiento con claridad y me dio mucha confianza. Los resultados fueron excelentes.',
      image: 'https://images.unsplash.com/photo-1582657233895-0f37a3f150c0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsYXRpbmElMjB3b21hbiUyMHNtaWxpbmclMjBwb3J0cmFpdHxlbnwxfHx8fDE3NzExMDgxOTR8MA&ixlib=rb-4.1.0&q=80&w=1080',
    },
  ];

  return (
    <section id="testimonios" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl mb-4 text-gray-900">Testimonios de Pacientes</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            La satisfacción de nuestros pacientes es nuestra mejor recomendación
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div 
              key={index} 
              className="bg-white p-8 rounded-xl shadow-lg relative"
            >
              <Quote className="w-10 h-10 text-blue-200 absolute top-6 right-6" />
              <div className="flex gap-1 mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-700 mb-6 relative z-10">
                "{testimonial.text}"
              </p>
              <div className="border-t pt-4 flex items-center gap-4">
                <ImageWithFallback
                  src={testimonial.image}
                  alt={testimonial.name}
                  className="w-14 h-14 rounded-full object-cover"
                />
                <div>
                  <p className="text-gray-900">{testimonial.name}</p>
                  <p className="text-sm text-gray-500">{testimonial.procedure}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}