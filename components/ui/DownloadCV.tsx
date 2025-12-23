"use client";

const DownloadCV = () => {
	const handleDownload = () => {
		const fileUrl = "/assets/CV.pdf";
		const link = document.createElement("a");
		link.href = fileUrl;
		link.download = "Alibek_Aitbekov_CV.pdf";
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	};

	return (
		<button
			onClick={handleDownload}
			className="w-12 h-12 flex items-center justify-center rounded-full hover:bg-purple/30 border border-white/20 hover:border-purple/50 transition-all duration-300 hover:scale-110"
			title="Download CV"
		>
			<svg
				width="20"
				height="20"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				strokeWidth="2"
				strokeLinecap="round"
				strokeLinejoin="round"
			>
				<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
				<polyline points="7 10 12 15 17 10" />
				<line x1="12" y1="15" x2="12" y2="3" />
			</svg>
		</button>
	);
};

export default DownloadCV;

