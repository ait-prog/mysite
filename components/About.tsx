"use client";

import Reveal from "./ui/Reveal";
import Sparkle from "./ui/Sparkle";
import { myTechStack, education } from "@/data";

const About = () => {
	return (
		<section id="about" className="py-20 relative">
			<Reveal>
				<h3 className="mb-4">
					About{" "}
					<span className="bg-gradient-to-r from-purple to-red-700 bg-clip-text text-transparent">
						me.
					</span>
				</h3>
			</Reveal>
			<div className="space-y-10">
				<Sparkle>
					<div className="bg-purple-900/[0.5] backdrop-blur-xl border border-white/[0.1] rounded-2xl p-8 md:p-12">
						<div className="space-y-6">
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
						</div>
					</div>
				</Sparkle>

				<Sparkle>
					<div className="bg-purple-900/[0.5] backdrop-blur-xl border border-white/[0.1] rounded-2xl p-8 md:p-12">
						<h4 className="text-2xl md:text-3xl font-bold mb-6">Tech Stack</h4>
						<div className="flex flex-wrap gap-3">
							{myTechStack.map((tech, index) => (
								<div
									key={index}
									className="bg-white/15 backdrop-blur-sm text-white text-sm font-semibold px-4 py-2 rounded-full shadow-lg hover:bg-purple/40 hover:border-purple/50 border border-white/20 transition-all duration-200 ease-in-out hover:scale-105 hover:shadow-purple/30"
								>
									{tech}
								</div>
							))}
						</div>
					</div>
				</Sparkle>

				<Sparkle>
					<div className="bg-purple-900/[0.5] backdrop-blur-xl border border-white/[0.1] rounded-2xl p-8 md:p-12">
						<h4 className="text-2xl md:text-3xl font-bold mb-6">Education</h4>
						<div className="space-y-2">
							<p className="text-xl font-semibold">{education.degree}</p>
							<p className="text-lg opacity-80">{education.school}</p>
							<p className="text-sm opacity-60">{education.period} • {education.location}</p>
						</div>
					</div>
				</Sparkle>
			</div>
		</section>
	);
};

export default About;

