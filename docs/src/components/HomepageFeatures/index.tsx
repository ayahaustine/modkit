import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  icon: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'FastAPI Backend',
    icon: '⚡',
    description: (
      <>
        Async Python with SQLAlchemy, Alembic migrations, JWT auth, and a
        built-in starlette-admin panel — ready to extend.
      </>
    ),
  },
  {
    title: 'Next.js Frontend',
    icon: '◊',
    description: (
      <>
        App Router, TypeScript, Tailwind CSS, and httpOnly cookie auth.
        Ships as a standalone Docker image.
      </>
    ),
  },
  {
    title: 'Production Ready',
    icon: '◎',
    description: (
      <>
        Docker Compose, PostgreSQL, nginx reverse proxy, and GitHub Actions
        CI with coverage reporting out of the box.
      </>
    ),
  },
];

function Feature({title, icon, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className={styles.featureCard}>
        <div className={styles.featureIcon}>{icon}</div>
        <Heading as="h3" className={styles.featureTitle}>
          {title}
        </Heading>
        <p className={styles.featureDesc}>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
