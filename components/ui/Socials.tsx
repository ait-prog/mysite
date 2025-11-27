"use client";

import React from "react";
import { socialMedia } from "@/data";

export const Socials = (): JSX.Element => (
  <div className="flex items-center gap-4">
    {socialMedia.map(({ id, link, img }) => (
      <a
        key={id}
        href={link}
        target="_blank"
        rel="noopener noreferrer"
        className="w-12 h-12 cursor-pointer flex justify-center items-center transform transition-all duration-300 ease-in-out hover:scale-110 group relative"
      >
        <div className="absolute inset-0 rounded-full bg-purple/0 group-hover:bg-purple/20 blur-md transition-all duration-300" />
        <img src={img} alt="social-icon" width={24} height={24} className="relative z-10 group-hover:brightness-125 transition-all duration-300" />
      </a>
    ))}
  </div>
);
