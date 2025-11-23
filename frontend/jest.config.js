/** @type {import('jest').Config} */
module.exports = {
    preset: 'ts-jest',
    testEnvironment: 'jsdom',
    roots: ['<rootDir>/src', '<rootDir>/tests'],
    moduleNameMapper: {
        '^@/(.*)$': '<rootDir>/src/$1',
    },
    setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
    transform: {
        '^.+\\.(ts|tsx)$': [
            'ts-jest',
            {
                tsconfig: {
                    module: 'commonjs',
                    jsx: 'react-jsx',
                    target: 'ES2022',
                },
                isolatedModules: true,
            },
        ],
    },
    testRegex: '(/__tests__/.*|(\\.|/)(test|spec))\\.(tsx?|jsx?)$',
    moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
    testPathIgnorePatterns: ["/node_modules/", "/.next/", ".*\\.integration\\.test\\."]
};
