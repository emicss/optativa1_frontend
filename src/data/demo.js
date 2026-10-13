export const clients = [
  {
    id: "CL-001",
    name: "Estudio Norte",
    contact: "Mariana López",
    email: "hola@estudionorte.example",
    initials: "EN",
    color: "sage",
    sector: "Diseño y arquitectura",
  },
  {
    id: "CL-002",
    name: "Casa Oliva",
    contact: "Diego Martínez",
    email: "admin@casaoliva.example",
    initials: "CO",
    color: "sand",
    sector: "Hospitalidad",
  },
  {
    id: "CL-003",
    name: "Lumina Digital",
    contact: "Andrea Ruiz",
    email: "equipo@lumina.example",
    initials: "LD",
    color: "lilac",
    sector: "Tecnología",
  },
  {
    id: "CL-004",
    name: "Grupo Terral",
    contact: "Roberto García",
    email: "contacto@terral.example",
    initials: "GT",
    color: "sky",
    sector: "Construcción",
  },
  {
    id: "CL-005",
    name: "Menta & Co.",
    contact: "Sofía Torres",
    email: "hola@menta.example",
    initials: "MC",
    color: "sage",
    sector: "Comercio",
  },
  {
    id: "CL-006",
    name: "Atelier Sur",
    contact: "Valeria Cruz",
    email: "estudio@ateliersur.example",
    initials: "AS",
    color: "sand",
    sector: "Diseño y arquitectura",
  },
];
export const services = [
  {
    id: "SRV-001",
    name: "Consultoría estratégica",
    category: "Consultoría",
    price: 2500,
    unit: "hora",
    icon: "users",
    description:
      "Diagnóstico y acompañamiento para llevar tu negocio al siguiente nivel.",
    tags: ["Sesión individual", "Reporte de resultados"],
    color: "sage",
  },
  {
    id: "SRV-002",
    name: "Diseño de identidad",
    category: "Diseño",
    price: 8500,
    unit: "proyecto",
    icon: "edit",
    description:
      "Una identidad visual consistente que expresa la esencia de cada marca.",
    tags: ["Manual de marca", "Archivos editables"],
    color: "lilac",
  },
  {
    id: "SRV-003",
    name: "Desarrollo web",
    category: "Tecnología",
    price: 18000,
    unit: "proyecto",
    icon: "grid",
    description:
      "Sitios a la medida, pensados para conectar con clientes y crecer.",
    tags: ["Diseño adaptable", "Entrega por etapas"],
    color: "sky",
  },
  {
    id: "SRV-004",
    name: "Soporte técnico",
    category: "Tecnología",
    price: 1200,
    unit: "mes",
    icon: "check",
    description:
      "Acompañamiento continuo para mantener tu operación en movimiento.",
    tags: ["Atención remota", "Seguimiento mensual"],
    color: "sky",
  },
  {
    id: "SRV-005",
    name: "Gestión de redes sociales",
    category: "Marketing",
    price: 6500,
    unit: "mes",
    icon: "users",
    description:
      "Contenido y planificación para construir una comunidad alrededor de tu marca.",
    tags: ["Calendario editorial", "Reporte mensual"],
    color: "sand",
  },
  {
    id: "SRV-006",
    name: "Producción fotográfica",
    category: "Diseño",
    price: 4200,
    unit: "sesión",
    icon: "eye",
    description:
      "Imágenes cuidadas para mostrar productos, espacios y nuevas ideas.",
    tags: ["Edición incluida", "Entrega digital"],
    color: "lilac",
  },
  {
    id: "SRV-007",
    name: "Capacitación de equipos",
    category: "Consultoría",
    price: 3800,
    unit: "sesión",
    icon: "book",
    description:
      "Talleres prácticos que convierten conocimientos en nuevas habilidades.",
    tags: ["Material de apoyo", "Sesión grupal"],
    color: "sage",
  },
  {
    id: "SRV-008",
    name: "Campaña publicitaria",
    category: "Marketing",
    price: 9000,
    unit: "campaña",
    icon: "arrow",
    description:
      "Estrategia, creatividad y seguimiento para alcanzar a tu audiencia.",
    tags: ["Plan de medios", "Análisis de resultados"],
    color: "sand",
  },
];
export const seedInvoices = [
  {
    id: "FAC-2026-0087",
    client: "CL-001",
    date: "2026-10-01",
    due: "2026-10-15",
    status: "Pendiente",
    lines: [
      {
        service: "SRV-002",
        qty: 1,
      },
    ],
  },
  {
    id: "FAC-2026-0086",
    client: "CL-002",
    date: "2026-09-29",
    due: "2026-10-13",
    status: "Pagada",
    lines: [
      {
        service: "SRV-005",
        qty: 1,
      },
    ],
  },
  {
    id: "FAC-2026-0085",
    client: "CL-003",
    date: "2026-09-26",
    due: "2026-09-30",
    status: "Vencida",
    lines: [
      {
        service: "SRV-003",
        qty: 1,
      },
    ],
  },
  {
    id: "FAC-2026-0084",
    client: "CL-004",
    date: "2026-09-24",
    due: "2026-10-08",
    status: "Pendiente",
    lines: [
      {
        service: "SRV-001",
        qty: 3,
      },
    ],
  },
  {
    id: "FAC-2026-0083",
    client: "CL-005",
    date: "2026-09-22",
    due: "2026-10-06",
    status: "Pagada",
    lines: [
      {
        service: "SRV-006",
        qty: 1,
      },
    ],
  },
  {
    id: "FAC-2026-0082",
    client: "CL-006",
    date: "2026-09-20",
    due: "2026-10-04",
    status: "Borrador",
    lines: [
      {
        service: "SRV-007",
        qty: 2,
      },
    ],
  },
  {
    id: "FAC-2026-0081",
    client: "CL-003",
    date: "2026-09-15",
    due: "2026-09-29",
    status: "Pagada",
    lines: [
      {
        service: "SRV-004",
        qty: 2,
      },
    ],
  },
];
