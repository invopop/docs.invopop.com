export const SvgComponent = ({size}) => {
  return (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 16 16"
    width={size}
    height={size}
  >
    <path
      fill="url(#a)"
      fillRule="evenodd"
      d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2Zm1 5v1.5h7c.84 0 1.397.26 1.737.578a1.598 1.598 0 0 1 0 2.344c-.34.319-.898.578-1.737.578H4.55v-.75h-1.5v2.25H10c1.16 0 2.103-.366 2.763-.984a3.097 3.097 0 0 0 0-4.532C12.103 5.366 11.161 5 10 5H3Z"
      clipRule="evenodd"
    />
    <defs>
      <linearGradient
        id="a"
        x1={15}
        x2={1}
        y1={15}
        y2={1}
        gradientUnits="userSpaceOnUse"
      >
        <stop offset={0.019} stopColor="#73BA72" />
        <stop offset={1} stopColor="#1FB3D1" />
      </linearGradient>
    </defs>
  </svg>
  )
}