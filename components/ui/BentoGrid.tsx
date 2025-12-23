"use client";

import { cn } from "@/lib/utils";
import React from "react";
import Sparkle from "./Sparkle";

export const BentoGrid = ({
	className,
	children,
}: {
	className?: string;
	children?: React.ReactNode;
}) => {
	return (
		<div
			className={cn(
				"grid md:auto-rows-[18rem] grid-cols-1 gap-4 max-w-7xl mx-auto",
				className
			)}
		>
			{children}
		</div>
	);
};

export const BentoGridItem = ({
	className,
	id,
	title,
	description,
	link,
	github,
	img,
	titleClassName,
	techs = [],
}: {
	className?: string;
	id?: number | string;
	title?: string | React.ReactNode;
	description?: string | React.ReactNode;
	link?: string;
	github?: string;
	img?: string;
	titleClassName?: string;
	techs?: string[];
}) => (
	<Sparkle
		duration={Math.floor(Math.random() * 10000) + 10000}
		as="div"
		className={cn("row-span-1 h-full w-full !flex !items-start !justify-start", className)}
	>
		<div className="h-full w-full group/bento flex flex-col items-start justify-start">
			<div className={cn(id === 6 && "flex justify-center", "h-full w-full flex-1")}>
				<div
					className={cn(
						titleClassName,
						"group-hover/bento:translate-x-2 transition duration-200 relative h-full w-full min-h-40 flex flex-col px-5 py-5 lg:py-10 z-10"
					)}
				>
					<div className="flex items-end gap-5 flex-1 w-full">
						{link && (
							<div className="space-y-10">
								<a
									href={link}
									target="_blank"
									rel="noopener noreferrer"
									className="cursor-pointer group/link z-20"
								>
									<div className="bg-white/10 backdrop-blur-sm rounded-lg p-2 hover:bg-purple/30 border border-white/20 hover:border-purple/50 transition-all duration-300 hover:scale-110 shadow-lg">
										<img
											src="/assets/link.svg"
											alt="External link"
											className="min-w-8 transform transition-all duration-300 ease-in-out"
										/>
									</div>
								</a>
							</div>
						)}

						<div className="space-y-6 flex-1">
							<p className="text-lg lg:text-3xl max-w-96 font-bold z-10 group-hover/bento:text-purple/90 transition-all duration-300">
								{title}
							</p>
							<p className="font-extralight md:max-w-[80%] md:text-xs lg:text-base text-sm z-10 opacity-80 group-hover/bento:opacity-100 transition-all duration-300">
								{description}
							</p>

							<div className="flex flex-wrap gap-2 py-1">
								{techs.map((tech) => (
									<div
										key={tech}
										className="bg-white/15 backdrop-blur-sm text-white text-sm font-semibold px-4 py-2 rounded-full shadow-lg hover:bg-purple/40 hover:border-purple/50 border border-white/20 transition-all duration-200 ease-in-out hover:scale-105 hover:shadow-purple/30"
									>
										{tech}
									</div>
								))}
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</Sparkle>
);

