import { Calendar, Phone } from 'lucide-react';
import { ImageWithFallback } from './figma/ImageWithFallback';
import Slider from 'react-slick';

export function Hero() {
  const scrollToContact = () => {
    const element = document.getElementById('contacto');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const scrollToAppointment = () => {
    const element = document.getElementById('separar-cita');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const sliderImages = [
    {
      url: 'https://images.unsplash.com/photo-1769072610024-5b8a50f05c73?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjBzdXJnZW9uJTIwZG9jdG9yfGVufDF8fHx8MTc3MTA3NjUxNHww&ixlib=rb-4.1.0&q=80&w=1080',
      alt: 'Dr. Boris Viafara',
    },
    {
      url: 'https://images.unsplash.com/photo-1758653500534-a47f6cd8abb0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBob3NwaXRhbCUyMG9wZXJhdGluZyUyMHJvb218ZW58MXx8fHwxNzcxMTA4MzEzfDA&ixlib=rb-4.1.0&q=80&w=1080',
      alt: 'Quirófano moderno',
    },
    {
      url: 'https://images.unsplash.com/photo-1758691461990-03b49d969495?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtZWRpY2FsJTIwY29uc3VsdGF0aW9uJTIwZG9jdG9yJTIwcGF0aWVudHxlbnwxfHx8fDE3NzEwODQ0ODh8MA&ixlib=rb-4.1.0&q=80&w=1080',
      alt: 'Consulta médica',
    },
    {
      url: 'https://images.unsplash.com/photo-1760600865625-dbf6a3acfb67?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdXJnaWNhbCUyMHRlYW0lMjBob3NwaXRhbHxlbnwxfHx8fDE3NzExMDgzMTR8MA&ixlib=rb-4.1.0&q=80&w=1080',
      alt: 'Equipo quirúrgico',
    },
  ];

  const sliderSettings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 4000,
    fade: true,
    cssEase: 'linear',
  };

  return (
    <section id="inicio" className="pt-20 bg-gradient-to-br from-blue-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-5xl mb-6 text-gray-900">
              Cirugía de Alta Especialidad
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Más de 15 años de experiencia brindando atención médica de excelencia con tecnología de vanguardia y un enfoque personalizado.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button 
                onClick={scrollToAppointment}
                className="bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition flex items-center justify-center gap-2"
              >
                <Calendar className="w-5 h-5" />
                Agendar Cita
              </button>
              <a 
                href="#contacto"
                onClick={(e) => {
                  e.preventDefault();
                  scrollToContact();
                }}
                className="border-2 border-blue-600 text-blue-600 px-8 py-4 rounded-lg hover:bg-blue-50 transition flex items-center justify-center gap-2"
              >
                <Phone className="w-5 h-5" />
                Llamar Ahora
              </a>
            </div>
          </div>
          <div className="relative">
            <div className="rounded-2xl overflow-hidden shadow-2xl">
              <Slider {...sliderSettings}>
                {sliderImages.map((image, index) => (
                  <div key={index}>
                    <ImageWithFallback
                      src={image.url}
                      alt={image.alt}
                      className="w-full h-auto"
                    />
                  </div>
                ))}
              </Slider>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}