import { nanoid } from 'nanoid';

export type User = {
  id: string;
  username: string;
  publicKey: string;
};

export type ImageAsset = {
  id: string;
  url: string;
  name: string;
  hash: string;
  signature: string;
  ownerId: string;
  createdAt: string;
  authenticityScore: number;
  history: {
    timestamp: string;
    action: 'CREATED' | 'TRANSFERRED' | 'MODIFIED' | 'VERIFIED';
    actor: string;
    hash: string;
  }[];
  metadata: {
    format: string;
    size: string;
    dimensions: string;
    aiProbability: number;
  };
};

export const generateHash = () => {
  return Array.from({ length: 64 }, () => 
    Math.floor(Math.random() * 16).toString(16)
  ).join('');
};

export const mockUser: User = {
  id: 'usr_' + nanoid(10),
  username: 'DemoUser',
  publicKey: '0x' + generateHash().substring(0, 40),
};

export const generateMockAsset = (file: File): ImageAsset => {
  const isAI = Math.random() > 0.8;
  return {
    id: 'asset_' + nanoid(10),
    url: URL.createObjectURL(file),
    name: file.name,
    hash: generateHash(),
    signature: 'sig_' + nanoid(32),
    ownerId: mockUser.id,
    createdAt: new Date().toISOString(),
    authenticityScore: isAI ? Math.floor(Math.random() * 40) + 20 : Math.floor(Math.random() * 15) + 85,
    history: [
      {
        timestamp: new Date().toISOString(),
        action: 'CREATED',
        actor: mockUser.publicKey,
        hash: generateHash(),
      }
    ],
    metadata: {
      format: file.type.split('/')[1].toUpperCase(),
      size: (file.size / 1024 / 1024).toFixed(2) + ' MB',
      dimensions: '1920x1080', // Mocked
      aiProbability: isAI ? Math.random() * 0.5 + 0.5 : Math.random() * 0.1,
    }
  };
};
