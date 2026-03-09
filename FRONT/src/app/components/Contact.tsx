import { MapPin, Phone, Mail, Clock } from 'lucide-react';

export function Contact() {
  return (
    <section id="contacto" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl mb-4 text-gray-900">Contacto</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Estamos aquí para responder tus preguntas y agendar tu consulta
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-12">
          {/* Información de Contacto */}
          <div>
            <h3 className="text-2xl mb-6 text-gray-900">Información de Contacto</h3>
            <div className="space-y-6">
              <div className="flex gap-4 items-start">
                <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0">
                  <MapPin className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="text-lg mb-1 text-gray-900">Dirección</h4>
                  <p className="text-gray-600">
                    Av. Paseo de la Reforma 476<br />
                    Colonia Juárez, CDMX 06600
                  </p>
                </div>
              </div>

              <div className="flex gap-4 items-start">
                <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Phone className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="text-lg mb-1 text-gray-900">Teléfono</h4>
                  <p className="text-gray-600">+52 55 1234 5678</p>
                  <p className="text-gray-600">+52 55 8765 4321</p>
                </div>
              </div>

              <div className="flex gap-4 items-start">
                <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Mail className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="text-lg mb-1 text-gray-900">Email</h4>
                  <p className="text-gray-600">contacto@drmendez.com</p>
                  <p className="text-gray-600">citas@drmendez.com</p>
                </div>
              </div>

              <div className="flex gap-4 items-start">
                <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Clock className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="text-lg mb-1 text-gray-900">Horario</h4>
                  <p className="text-gray-600">Lunes a Viernes: 9:00 - 19:00</p>
                  <p className="text-gray-600">Sábados: 9:00 - 14:00</p>
                  <p className="text-gray-600">Emergencias: 24/7</p>
                </div>
              </div>
            </div>
          </div>

          {/* Mapa de Google Maps */}
          <div>
            <h3 className="text-2xl mb-6 text-gray-900">Ubicación</h3>
            <div className="rounded-xl overflow-hidden shadow-lg h-[500px]">
              <iframe
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3762.4857837419817!2d-99.17066492462736!3d19.428227681868676!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x85d1ff3b3f3e3b3b%3A0x3b3b3b3b3b3b3b3b!2sAv.%20Paseo%20de%20la%20Reforma%20476%2C%20Ju%C3%A1rez%2C%20Cuauht%C3%A9moc%2C%2006600%20Ciudad%20de%20M%C3%A9xico%2C%20CDMX!5e0!3m2!1ses!2smx!4v1234567890123!5m2!1ses!2smx"
                width="100%"
                height="100%"
                style={{ border: 0 }}
                allowFullScreen
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                title="Ubicación del consultorio"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}