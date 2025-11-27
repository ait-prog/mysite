import Button from "./ui/Button";
import Reveal from "./ui/Reveal";
import { Spotlight } from "./ui/Spotlight";

const Hero = () => {
  return (
    <div className="pb-20 pt-36 relative">
      <div>
        <Spotlight
          className="-top-40 -left-10 md:-left-32 md:-top-20 h-screen"
          fill="white"
        />
        <Spotlight
          className="h-[100vh] w-[50vw] top-10 left-full"
          fill="purple"
        />
        <Spotlight className="left-80 top-28 h-[100vh] w-[50vw]" fill="purple" />
      </div>
      <div className="text-center my-20 mx-auto max-w-[900px] justify-center flex flex-col relative z-10">
        <Reveal>
          <h1 className="text-center text-4xl md:text-6xl lg:text-8xl font-extrabold relative">
            Hey, I&apos;m {''}
            <span className="bg-gradient-to-r from-purple to-red-700 bg-clip-text text-transparent">
              Alibek Aitbekov!
            </span>
          </h1>
        </Reveal>
        <Reveal>
          <h2 className="title my-6 text-xl md:text-3xl lg:text-5xl">
            I&apos;m a <span className="bg-gradient-to-r from-purple to-red-700 bg-clip-text text-transparent">MLOps / ML Engineer</span>
          </h2>
        </Reveal>
        <Reveal>
          <p className="max-w-[700px] mx-auto opacity-90">
            Passionate about building intelligent systems and deploying machine learning models at scale. I specialize in MLOps, deep learning, and Web3 technologies. Currently studying Statistics and Data Science while working on cutting-edge ML projects. Let&apos;s connect and build something amazing together!
          </p>
        </Reveal>
        <Reveal>
          <a className="mt-10 mx-auto" href="#contact">
            <Button
              title="Contact me"
              icon={<img src="/assets/send.svg" />}
              position="right"
            />
          </a>
        </Reveal>
      </div>
    </div>
  );
};

export default Hero;
