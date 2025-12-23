"use client";

import Reveal from "./ui/Reveal";
import Sparkle from "./ui/Sparkle";
import { workExperience } from "@/data";

const Experience = () => {
	return (
		<section id="experience" className="py-20 relative">
			<Reveal>
				<h3 className="mb-4">
					Work{" "}
					<span className="bg-gradient-to-r from-purple to-red-700 bg-clip-text text-transparent">
						Experience.
					</span>
				</h3>
			</Reveal>
			<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
				{workExperience.map((exp) => (
					<Sparkle key={exp.id}>
						<div className="bg-purple-900/[0.5] backdrop-blur-xl border border-white/[0.1] rounded-2xl p-8 md:p-12 h-full">
							<div className="space-y-4">
								<div>
									<h4 className="text-2xl md:text-3xl font-bold mb-2">{exp.title}</h4>
									<p className="text-xl font-semibold text-purple/90 mb-1">{exp.company}</p>
									<p className="text-sm opacity-60">{exp.period} • {exp.location}</p>
								</div>
								<p className="opacity-80">{exp.desc}</p>
								<div className="flex flex-wrap gap-2 pt-2">
									{exp.skills.map((skill, index) => (
										<div
											key={index}
											className="bg-white/15 backdrop-blur-sm text-white text-xs font-semibold px-3 py-1 rounded-full shadow-lg hover:bg-purple/40 hover:border-purple/50 border border-white/20 transition-all duration-200 ease-in-out"
										>
											{skill}
										</div>
									))}
								</div>
							</div>
						</div>
					</Sparkle>
				))}
			</div>
		</section>
	);
};

export default Experience;

