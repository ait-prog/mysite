"use client";

import { cn } from "@/lib/utils";
import React from "react";

interface SparkleProps {
	children: React.ReactNode;
	className?: string;
	duration?: number;
	as?: keyof JSX.IntrinsicElements;
}

const Sparkle: React.FC<SparkleProps> = ({
	children,
	className,
	duration = 10000,
	as: Component = "div",
}) => {
	return (
		<Component
			className={cn(
				"relative group",
				className
			)}
			style={{
				boxShadow: "0 0 20px rgba(155, 77, 150, 0.3)",
			}}
			onMouseEnter={(e: React.MouseEvent<HTMLElement>) => {
				e.currentTarget.style.boxShadow = "0 0 40px rgba(155, 77, 150, 0.6)";
			}}
			onMouseLeave={(e: React.MouseEvent<HTMLElement>) => {
				e.currentTarget.style.boxShadow = "0 0 20px rgba(155, 77, 150, 0.3)";
			}}
		>
			{children}
		</Component>
	);
};

export default Sparkle;

