import React from "react";
import { Sparkle } from "./ui/Sparkle";
import { myTechStack, education } from "@/data";
import Reveal from "./ui/Reveal";

const About = () => (
  <section id="about" className="py-20 w-full space-y-10">
    <Reveal>
      <h3 className="mb-10">
        About{' '}
        <span className="bg-gradient-to-r from-purple to-red-700 bg-clip-text text-transparent">
          me.
        </span>
      </h3>
    </Reveal>
    <div className="sm:flex grid-cols-[2fr_1fr] gap-6 space-y-5 sm:space-y-0">
      <Sparkle
        duration={Math.floor(Math.random() * 10000) + 10000}
        className="flex-col text-left p-3 md:p-5 lg:p-10 gap-5 min-h-full"
      >
        <p>
          Hey! I&apos;m Alibek Aitbekov, a Machine Learning Engineer and Math Science student passionate about building reliable, robust, and intelligent systems.
        </p>
        <p>
          Currently pursuing a Bachelor&apos;s degree in Math Science, I combine strong theoretical foundations with hands-on experience in machine learning, deep learning, and statistical modeling. I love exploring how we can make modern ML systems more trustworthy through rigorous analysis, probabilistic methods, and better representations.
        </p>
        <p>
          I&apos;ve worked on everything from creating custom regression models and building libraries from scratch to improving real-world ML systems during my internship at MyCarDigital. I enjoy tackling challenging problems that require both mathematical depth and creative engineering.
        </p>
        <p>
          Whether it&apos;s developing self-supervised models, analyzing neural networks through mathematical morphisms, or building AI tools and chatbots for platforms like Discord, I&apos;m always excited to push the boundaries of what&apos;s possible.
        </p>
        <p>
          If you&apos;re interested in machine learning, mathematics, or building the future of robust AI systems — let&apos;s connect!
        </p>
      </Sparkle>

      <div className="flex flex-col gap-6">
        <div
          className="relative overflow-hidden rounded-3xl border border-white/[0.1] transition duration-200 shadow-input dark:shadow-none flex flex-col space-y-4 p-10 group hover:border-purple/50"
        >
          <p className="text-lg lg:text-3xl font-extrabold">
            <span className="bg-gradient-to-r from-purple to-red-700 bg-clip-text text-transparent">
              My tech Stack!
            </span>
          </p>

          <div className="flex flex-wrap gap-3 py-4">
            {myTechStack.map((skill) => (
              <div
                key={skill}
                className="bg-white/10 text-white text-sm font-semibold px-4 py-2 rounded-full shadow-lg hover:bg-purple/30 hover:border-purple/50 border border-transparent transition-all duration-200 ease-in-out hover:scale-105"
              >
                {skill}
              </div>
            ))}
          </div>
        </div>

        <div
          className="relative overflow-hidden rounded-3xl border border-white/[0.1] transition duration-200 shadow-input dark:shadow-none flex flex-col space-y-3 p-6 group hover:border-purple/50"
        >
          <p className="text-lg lg:text-xl font-extrabold">
            <span className="bg-gradient-to-r from-purple to-red-700 bg-clip-text text-transparent">
              Education
            </span>
          </p>
          <div className="space-y-2">
            <p className="text-sm font-semibold">{education.degree}</p>
            <p className="text-sm opacity-80">{education.school}</p>
            <p className="text-xs opacity-60">{education.period} • {education.location}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
);

export default About;
