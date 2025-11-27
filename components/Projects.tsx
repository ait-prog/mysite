"use client";

import { projects } from "@/data";
import { BentoGrid, BentoGridItem } from "./ui/BentoGrid";
import Reveal from "./ui/Reveal";

const Projects = () => {
  return (
    <section id="projects" className="py-20 relative">
      <Reveal>
         <h3 className="mb-4">
          Recent{" "}
          <span className="bg-gradient-to-r from-purple to-red-700 bg-clip-text text-transparent">
            projects.</span>
        </h3>
      </Reveal>
      <BentoGrid className="w-full py-20">
        {projects.map((item, i) => (
          <BentoGridItem
            key={item.id}
            {...item}
            techs={item.techs}
          />
        ))}
      </BentoGrid>
    </section>
  );
};

export default Projects;
