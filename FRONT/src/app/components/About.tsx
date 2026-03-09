import {
  Award,
  GraduationCap,
  Users,
  Heart,
  CheckCircle,
} from "lucide-react";
import { ImageWithFallback } from './figma/ImageWithFallback';

export function About() {
  const certifications = [
    "Certificación del Consejo Mexicano de Cirugía General",
    "Fellow del American College of Surgeons (FACS)",
    "Certificación en Cirugía Laparoscópica Avanzada",
    "Certificación en Cirugía Bariátrica y Metabólica",
  ];

  const courses = [
    "Curso Avanzado de Cirugía Mínimamente Invasiva - Hospital General de México",
    "Diplomado en Cirugía Oncológica - Instituto Nacional de Cancerología",
    "Curso Internacional de Cirugía Robótica - Johns Hopkins University",
    "Especialización en Cirugía de Tiroides y Paratiroides - MD Anderson Cancer Center",
    "Curso de Actualización en Cirugía de Urgencias - UNAM",
    "Diplomado en Gestión y Calidad en Servicios de Salud",
  ];

  return (
    <section id="sobre-mi" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl mb-4 text-gray-900">
            Sobre el Dr. Boris Viafara
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Cirujano certificado comprometido con la excelencia
            médica y el bienestar de cada paciente
          </p>
        </div>

        {/* Foto y descripción */}
        <div className="grid md:grid-cols-2 gap-12 items-center mb-16">
          <div className="order-2 md:order-1">
            <p className="text-lg text-gray-700 mb-6">
              Con más de 15 años de experiencia en cirugía
              general y especializada, el Dr. Boris Viafara ha
              dedicado su carrera a proporcionar atención médica
              de la más alta calidad.
            </p>
            <p className="text-lg text-gray-700 mb-6">
              Graduado de la Universidad Nacional Autónoma de
              México (UNAM) y con especialización en el Hospital
              General de México, el Dr. Viafara se ha mantenido a
              la vanguardia de las técnicas quirúrgicas más
              innovadoras.
            </p>
            <p className="text-lg text-gray-700">
              Su enfoque combina experiencia técnica con un
              trato humano y personalizado, asegurando que cada
              paciente reciba la atención integral que merece.
            </p>
          </div>
          <div className="order-1 md:order-2">
            <div className="rounded-2xl overflow-hidden shadow-xl">
              <ImageWithFallback
                src="https://images.unsplash.com/photo-1762237798212-bcc000c00891?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjBtYWxlJTIwc3VyZ2VvbiUyMHBvcnRyYWl0fGVufDF8fHx8MTc3MTEwNzkzN3ww&ixlib=rb-4.1.0&q=80&w=1080"
                alt="Dr. Boris Viafara"
                className="w-full h-auto"
              />
            </div>
          </div>
        </div>

        {/* Estadísticas */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          <div className="bg-blue-50 p-6 rounded-xl text-center">
            <Award className="w-12 h-12 text-blue-600 mb-4 mx-auto" />
            <h3 className="text-2xl mb-2 text-gray-900">
              15+
            </h3>
            <p className="text-gray-600">
              Años de Experiencia
            </p>
          </div>
          <div className="bg-blue-50 p-6 rounded-xl text-center">
            <Users className="w-12 h-12 text-blue-600 mb-4 mx-auto" />
            <h3 className="text-2xl mb-2 text-gray-900">
              5000+
            </h3>
            <p className="text-gray-600">Cirugías Exitosas</p>
          </div>
          <div className="bg-blue-50 p-6 rounded-xl text-center">
            <GraduationCap className="w-12 h-12 text-blue-600 mb-4 mx-auto" />
            <h3 className="text-2xl mb-2 text-gray-900">
              Certificado
            </h3>
            <p className="text-gray-600">Consejo Mexicano</p>
          </div>
          <div className="bg-blue-50 p-6 rounded-xl text-center">
            <Heart className="w-12 h-12 text-blue-600 mb-4 mx-auto" />
            <h3 className="text-2xl mb-2 text-gray-900">
              98%
            </h3>
            <p className="text-gray-600">Satisfacción</p>
          </div>
        </div>

        {/* Certificaciones y Cursos */}
        <div className="grid md:grid-cols-2 gap-12">
          {/* Certificaciones */}
          <div className="bg-gray-50 p-8 rounded-xl">
            <h3 className="text-2xl mb-6 text-gray-900 flex items-center gap-3">
              <Award className="w-8 h-8 text-blue-600" />
              Certificaciones
            </h3>
            <ul className="space-y-4">
              {certifications.map((cert, index) => (
                <li key={index} className="flex gap-3 items-start">
                  <CheckCircle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">{cert}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Cursos y Especializaciones */}
          <div className="bg-gray-50 p-8 rounded-xl">
            <h3 className="text-2xl mb-6 text-gray-900 flex items-center gap-3">
              <GraduationCap className="w-8 h-8 text-blue-600" />
              Cursos y Especializaciones
            </h3>
            <ul className="space-y-4">
              {courses.map((course, index) => (
                <li key={index} className="flex gap-3 items-start">
                  <CheckCircle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">{course}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}