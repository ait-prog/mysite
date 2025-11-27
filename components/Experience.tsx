import React from "react";
import { workExperience } from "@/data";
import { Sparkle } from "./ui/Sparkle";

const Experience = (): JSX.Element => (
  <section id="experience" className="sm:py-20 w-full relative">
    <h3 className="title">
      My{' '}
      <span className="bg-gradient-to-r from-purple to-red-700 bg-clip-text text-transparent">
        experience.
      </span>
    </h3>

    <div className="w-full mt-12 space-y-10 relative">
      {/* Timeline line */}
      <div className="hidden md:block absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-purple/50 via-purple to-purple/50 opacity-30" />
      
      {workExperience.map(({ id, company, title, period, location, desc, skills }, index) => (
        <div key={id} className="relative">
          {/* Timeline dot */}
          <div className="hidden md:block absolute left-6 top-6 w-4 h-4 rounded-full bg-purple border-4 border-[#120012] z-10 shadow-lg shadow-purple/50" />
          
          <Sparkle duration={Math.floor(Math.random() * 10000) + 10000}>
            <div className="p-3 md:p-5 lg:p-10 md:ml-16 group">
              <div className="text-start relative">
                <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-purple/0 via-purple/5 to-purple/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10" />

                <div className="flex flex-col md:flex-row md:justify-between gap-4">
                  <div>
                    <h3 className="text-justify text-lg lg:text-3xl font-extrabold">{company}</h3>
                    <p className="text-xl md:text-2xl font-bold mt-3">
                      <span className="bg-gradient-to-r from-purple to-red-700 bg-clip-text text-transparent">
                        {title}
                      </span>
                    </p>
                  </div>

                  <div className="text-start md:text-end opacity-80">
                    <p className="font-semibold">{period}</p>
                    <p>{location}</p>
                  </div>
                </div>

                <p className="my-5 opacity-90">{desc}</p>

                <div className="flex flex-wrap gap-2 mt-10">
                  {skills.map((skill) => (
                    <div
                      key={skill}
                      className="bg-white/10 text-sm font-semibold px-4 py-2 rounded-full shadow-lg hover:bg-purple/30 hover:border-purple/50 border border-transparent transition-all duration-200 ease-in-out hover:scale-105"
                    >
                      {skill}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Sparkle>
        </div>
      ))}
    </div>
  </section>
);

export default Experience;
